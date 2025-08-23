"""Mijia device adapter based on MijiaAPI"""
from typing import Dict, List, Any, Optional
from mijiaAPI import mijiaAPI, mijiaDevice, mijiaLogin, get_device_info
from config.mijia_config import load_mijia_config, MijiaConfig
from utils.logger import get_logger
from utils.auth_manager import AuthDataManager
import traceback
from datetime import datetime
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from qrcode import QRCode

_LOGGER = get_logger(__name__)

class MijiaAdapter:
    """Mijia device adapter"""

    def __init__(self):
        """Initialize adapter"""
        self._api: Optional[mijiaAPI] = None
        self._auth_data: Optional[Dict[str, Any]] = None
        self._connected = False
        self._devices: Dict[str, mijiaDevice] = {}
        self._config: Optional[MijiaConfig] = None
        self._device_status_cache: Dict[str, Dict[str, Any]] = {}
        self._last_status_update: Optional[datetime] = None
        self._config = load_mijia_config()
        self._auth_manager = AuthDataManager()
        # Patch mijiaAPI to avoid encoding issues with QR code display
        self._patch_qr_display()
    
    def _patch_qr_display(self):
        """Patch mijiaAPI's QR display method to avoid encoding issues
        
        The original mijiaAPI._print_qr method tries to print Unicode block characters
        to the terminal using qr.print_ascii(), which causes GBK encoding errors on
        systems where the default encoding can't handle these characters.
        
        This patch replaces the method to only save the QR code as a PNG file,
        avoiding the problematic ASCII output while maintaining functionality.
        """
        def safe_print_qr(loginurl: str, box_size: int = 10) -> None:
            """Safe QR code display that avoids encoding issues"""
            _LOGGER.info('请使用米家APP扫描二维码')
            _LOGGER.info('QR code will be saved as qr.png in current directory')
            try:
                qr = QRCode(border=1, box_size=box_size)
                qr.add_data(loginurl)
                qr.make_image().save('qr.png')
                _LOGGER.info('QR code saved successfully as qr.png')
                # 尝试显示二维码图片
                try:
                    img = Image.open('qr.png')
                    img.show()
                except Exception as e:
                    _LOGGER.error(f'Failed to show QR code: {e}')

                # 尝试打印二维码到终端
                try:
                    qr.print_ascii(invert=True, tty=True)
                except Exception as e:
                    _LOGGER.error(f'Failed to print QR code in terminal, saving as image only {e}')
                
            except Exception as e:
                _LOGGER.error(f'Failed to save QR code: {e}')
                raise
        
        # Replace the problematic _print_qr method
        mijiaLogin._print_qr = staticmethod(safe_print_qr)
        
    async def connect(self) -> bool:
        """Connect to Mijia cloud service

        Returns:
            bool: Whether connection is successful
        """
        try:
            _LOGGER.info("Starting connection to Mijia cloud service...")
            
            if not self._config:
                error_msg = "Mijia configuration not loaded, please check config file or environment variables"
                _LOGGER.error(error_msg)
                raise ValueError(error_msg)

            login = mijiaLogin()
            auth_data = self._auth_manager.load()
            
            if auth_data and self._auth_manager.validate(auth_data):
                self._auth_data = auth_data
                _LOGGER.info("Successfully loaded and validated authentication data from file")
            else:
                if auth_data:
                    _LOGGER.warning("Cached authentication data is invalid, starting fresh login...")
                    self._auth_manager.clear()
                else:
                    _LOGGER.info("No cached authentication data found, starting login...")
                
                if self._config.enableQR:
                    _LOGGER.info("Using QR code login mode")
                    self._auth_data = login.QRlogin()
                else:
                    _LOGGER.info(f"Using username/password login: {self._config.username}")
                    if not self._config.username or not self._config.password:
                        error_msg = "Username or password is empty, please check configuration"
                        _LOGGER.error(error_msg)
                        raise ValueError(error_msg)
                    
                    self._auth_data = login.login(self._config.username, self._config.password)

                if self._auth_data:
                    if self._auth_manager.save(self._auth_data):
                        _LOGGER.info("Login successful, authentication data saved")
                    else:
                        _LOGGER.warning("Login successful, but failed to save authentication data")
                else:
                    error_msg = "Login failed, authentication data not obtained"
                    _LOGGER.error(error_msg)
                    raise RuntimeError(error_msg)
            
            # 使用认证数据初始化 API
            _LOGGER.info("Initializing Mijia API...")
            self._api = mijiaAPI(self._auth_data)
            
            # 检查 API 是否可用
            if self._api.available:
                self._connected = True
                _LOGGER.info("Successfully connected to Mijia cloud service")
                return True
            else:
                error_msg = "Mijia API unavailable, possibly due to expired authentication data or network issues"
                _LOGGER.error(error_msg)
                # 清除可能过期的认证数据
                self._auth_data = None
                if self._auth_manager.clear():
                    _LOGGER.info("Expired authentication data cleared")
                else:
                    _LOGGER.warning("Failed to clear expired authentication data")
                
                raise RuntimeError(error_msg)
                
        except Exception as e:
            error_msg = f"Failed to connect to Mijia cloud service: {str(e)}"
            _LOGGER.error(error_msg)
            _LOGGER.debug(f"Detailed error information: {traceback.format_exc()}")
            
            # 重置连接状态
            self._connected = False
            self._api = None
            
            return False

    async def disconnect(self):
        """Disconnect"""
        try:
            self._api = None
            self._auth_data = None
            self._connected = False
            self._devices.clear()
            _LOGGER.info("Disconnected from Mijia cloud service")
        except Exception as e:
            _LOGGER.error(f"Error during disconnection: {e}")
    
    def clear_auth_data(self) -> bool:
        """清除认证数据
        
        Returns:
            bool: 是否清除成功
        """
        self._auth_data = None
        return self._auth_manager.clear()
    
    def has_valid_auth_data(self) -> bool:
        """检查是否有有效的认证数据
        
        Returns:
            bool: 是否有有效的认证数据
        """
        if self._auth_data:
            return self._auth_manager.validate(self._auth_data)
        return self._auth_manager.exists() and self._auth_manager.validate()
    
    def get_auth_file_path(self) -> Path:
        """获取认证数据文件路径
        
        Returns:
            Path: 认证数据文件路径
        """
        return self._auth_manager.get_file_path()
    
    def _create_device_sync(self, device_data: Dict[str, Any], index: int) -> tuple:
        """同步创建设备对象的辅助方法
        
        Args:
            device_data: 设备数据
            index: 设备索引
            
        Returns:
            tuple: (success: bool, device: mijiaDevice or None, error_info: str or None)
        """
        try:
            did = device_data.get("did")
            if not did:
                return False, None, f"Device{index}(missing did)"
            
            model = device_data.get("model")
            if not model:
                return False, None, f"Device{index}(missing model)"
            
            # 获取设备信息（这是耗时操作）
            dev_info = get_device_info(model)
            device = mijiaDevice(self._api, dev_info=dev_info, did=did)
            
            return True, device, None
            
        except Exception as e:
            device_name = device_data.get('name', f'Device{index}')
            return False, None, device_name
    
    async def discover_devices(self, max_workers: int = 5) -> List[mijiaDevice]:
        """Discover devices with concurrent processing
        
        Args:
            max_workers: 最大并发工作线程数，默认为5

        Returns:
            List[mijiaDevice]: List of discovered devices
        """
        if not self._connected or not self._api:
            error_msg = "Not connected to Mijia cloud service, please call connect() method first"
            _LOGGER.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            _LOGGER.info("Starting Mijia device discovery...")
            
            # 获取设备列表
            raw_device_infos = self._api.get_devices_list()
            
            if not raw_device_infos:
                _LOGGER.warning("No devices discovered")
                return []
            
            _LOGGER.info(f"Retrieved {len(raw_device_infos)} device information from cloud")
            _LOGGER.info(f"Using concurrent processing with {max_workers} workers to optimize performance")
            
            device_infos = []
            failed_devices = []
            
            # 使用线程池并发处理设备信息获取
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_index = {
                    executor.submit(self._create_device_sync, device_data, i): i 
                    for i, device_data in enumerate(raw_device_infos)
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        success, device, error_info = future.result()
                        
                        if success and device:
                            self._devices[device.did] = device
                            device_infos.append(device)
                            _LOGGER.debug(f"Successfully created device object: {device.name} ({device.did})")
                        else:
                            failed_devices.append(error_info or f"Device{index}")
                            _LOGGER.warning(f"Failed to create device {index}: {error_info}")
                            
                    except Exception as e:
                        failed_devices.append(f"Device{index}")
                        _LOGGER.warning(f"Exception processing device {index}: {e}")
            
            success_count = len(device_infos)
            failed_count = len(failed_devices)
            
            if success_count > 0:
                device_names = [device.name for device in device_infos]
                _LOGGER.info(f"Successfully discovered {success_count} devices: {device_names}")
            
            if failed_count > 0:
                _LOGGER.warning(f"{failed_count} devices failed to create: {failed_devices}")
            
            return device_infos
            
        except Exception as e:
            error_msg = f"Failed to discover devices: {str(e)}"
            _LOGGER.error(error_msg)
            _LOGGER.debug(f"Detailed error information: {traceback.format_exc()}")
            raise RuntimeError(error_msg) from e

    async def get_device_properties(self, device_id: str) -> List:
        """Get device property list

        Args:
            device_id: Device ID

        Returns:
            List: Device property list
        """
        device = self._get_device(device_id)
        
        try:
            # Get device specification information
            propsMap = device.prop_list
            if not propsMap:
                return []
            return list(map(lambda x: x, propsMap.values()))
        except Exception as e:
            _LOGGER.error(f"Failed to get device properties for {device_id}: {e}")
            raise
    
    async def get_device_actions(self, device_id: str) -> List:
        """Get device action list

        Args:
            device_id: Device ID

        Returns:
            List: Device action list
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        if device_id not in self._devices:
            raise ValueError(f"Device {device_id} not found")
        
        try:
            device = self._devices[device_id]
            if not device.action_list:
                return []
            return list(map(lambda x: x, device.action_list.values()))
        except Exception as e:
            _LOGGER.error(f"Failed to get device operations: {e}")
            raise
    
    async def get_property_value(self, device_id: str, siid: int, piid: int) -> Any:
        """Get device property value

        Args:
            device_id: Device ID
            siid: Service instance ID
            piid: Property instance ID

        Returns:
            Any: Property value
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        try:
            # Use API to get property directly
            result = self._api.get_devices_prop([{
                "did": device_id,
                "siid": siid,
                "piid": piid
            }])
            
            if result and len(result) > 0:
                prop_result = result[0]
                if prop_result.get('code') == 0:
                    return prop_result.get('value')
                else:
                    raise RuntimeError(f"Failed to get property: {prop_result.get('code')}")
            else:
                raise RuntimeError("No result returned")
                
        except Exception as e:
            _LOGGER.error(f"Failed to get property value: {e}")
            raise
    
    async def set_property_value(self, device_id: str, siid: int, piid: int, value: Any) -> bool:
        """Set device property value

        Args:
            device_id: Device ID
            siid: Service instance ID
            piid: Property instance ID
            value: Value to set

        Returns:
            bool: Whether setting is successful
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        try:
            # Use API to set property directly
            result = self._api.set_devices_prop([{
                "did": device_id,
                "siid": siid,
                "piid": piid,
                "value": value
            }])
            
            if result and len(result) > 0:
                prop_result = result[0]
                success = prop_result.get('code') == 0
                if success:
                    _LOGGER.info(f"Successfully set property {siid}:{piid} = {value} (device: {device_id})")
                else:
                    _LOGGER.warning(f"Failed to set property {siid}:{piid} = {value} (device: {device_id}), error code: {prop_result.get('code')}")
                return success
            else:
                return False
                
        except Exception as e:
            _LOGGER.error(f"Failed to set property value: {e}")
            raise
    
    async def call_action(self, device_id: str, siid: int, aiid: int, params: List[Any] = None) -> List[Any]:
        """Execute device action

        Args:
            device_id: Device ID
            siid: Service instance ID
            aiid: Action instance ID
            params: Action parameters

        Returns:
            List[Any]: Action result
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        try:
            # Use API to execute action directly
            result = self._api.run_action({
                "did": device_id,
                "siid": siid,
                "aiid": aiid,
                "in": params or []
            })
            
            if result.get('code') == 0:
                _LOGGER.info(f"Successfully executed action {siid}:{aiid} (device: {device_id})")
                return result.get('out', [])
            else:
                raise RuntimeError(f"Action execution failed, error code: {result.get('code')}")
                
        except Exception as e:
            _LOGGER.error(f"Failed to execute action: {e}")
            raise
    
    async def get_homes(self) -> List[Dict[str, Any]]:
        """Get home list

        Returns:
            List[Dict[str, Any]]: Home list
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        try:
            homes = self._api.get_homes_list()
            return homes
        except Exception as e:
            _LOGGER.error(f"Failed to get home list: {e}")
            raise

    async def get_scenes_list(self, home_id: str) -> List[Dict[str, Any]]:
        """Get scene list

        Args:
            home_id: Home ID

        Returns:
            List[Dict[str, Any]]: Scene list
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        try:
            scenes = self._api.get_scenes_list(home_id)
            return scenes
        except Exception as e:
            _LOGGER.error(f"Failed to get scene list: {e}")
            raise

    async def run_scene(self, scene_id: str) -> bool:
        """Run scene

        Args:
            scene_id: Scene ID

        Returns:
            bool: Whether running is successful
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        try:
            return await self._api.run_scene(scene_id)
        except Exception as e:
            _LOGGER.error(f"Failed to run scene: {e}")
            raise

    async def get_consumable_items(self, home_id: str, owner_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get consumable item list

        Args:
            home_id (str): home_id from get_homes_list
            owner_id (int, optional): UserID,default is None, provide owner_id when home_id is shared

        Returns:
            List[Dict[str, Any]]: Consumable item list
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        try:
            items = self._api.get_consumable_items(home_id, owner_id)
            return items
        except Exception as e:
            _LOGGER.error(f"Failed to get consumable item list: {e}")
            raise

    def _get_device(self, device_id: str) -> mijiaDevice:
        """Get device object

        Args:
            device_id: Device ID

        Returns:
            mijiaDevice: Device object

        Raises:
            RuntimeError: If device does not exist or not connected
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        if device_id not in self._devices:
            raise RuntimeError(f"Device {device_id} not found. Please discover devices first.")
        
        return self._devices[device_id]
    
    @property
    def connected(self) -> bool:
        """Whether connected"""
        return self._connected
    
    @property
    def device_count(self) -> int:
        """Device count"""
        return len(self._devices)
    
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status information

        Args:
            device_id: Device ID

        Returns:
            Dict[str, Any]: Device status information
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        try:
            device = self._get_device(device_id)
            
            # Get device basic information
            status_info = {
                "device_id": device_id,
                "name": device.name,
                "model": device.model,
                "online": getattr(device, 'online', True),
                "room_id": getattr(device, 'room_id', None),
                "spec_type": getattr(device, 'spec_type', None),
                "last_update": datetime.now().isoformat()
            }
            
            # Cache status information
            self._device_status_cache[device_id] = status_info
            self._last_status_update = datetime.now()
            
            _LOGGER.debug(f"Successfully retrieved device status: {device.name} ({device_id})")
            return status_info
            
        except Exception as e:
            error_msg = f"Failed to get device status {device_id}: {str(e)}"
            _LOGGER.error(error_msg)
            _LOGGER.debug(f"Detailed error information: {traceback.format_exc()}")
            raise RuntimeError(error_msg) from e
    
    async def refresh_all_device_status(self) -> Dict[str, Dict[str, Any]]:
        """Refresh all device status

        Returns:
            Dict[str, Dict[str, Any]]: Status information of all devices
        """
        if not self._connected:
            raise RuntimeError("Not connected to Mijia cloud service")
        
        try:
            _LOGGER.info("Starting to refresh all device status...")
            
            status_results = {}
            failed_devices = []
            
            for device_id in self._devices.keys():
                try:
                    status = await self.get_device_status(device_id)
                    status_results[device_id] = status
                except Exception as e:
                    _LOGGER.warning(f"Failed to refresh device status {device_id}: {e}")
                    failed_devices.append(device_id)
                    continue
            
            success_count = len(status_results)
            failed_count = len(failed_devices)
            
            _LOGGER.info(f"Device status refresh completed: {success_count} successful, {failed_count} failed")
            
            if failed_count > 0:
                _LOGGER.warning(f"Failed to refresh devices: {failed_devices}")
            
            return status_results
            
        except Exception as e:
            error_msg = f"Failed to refresh all device status: {str(e)}"
            _LOGGER.error(error_msg)
            _LOGGER.debug(f"Detailed error information: {traceback.format_exc()}")
            raise RuntimeError(error_msg) from e
    
    def get_cached_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get cached device status

        Args:
            device_id: Device ID

        Returns:
            Optional[Dict[str, Any]]: Cached device status, returns None if not exists
        """
        return self._device_status_cache.get(device_id)
    
    def get_all_cached_device_status(self) -> Dict[str, Dict[str, Any]]:
        """Get all cached device status

        Returns:
            Dict[str, Dict[str, Any]]: All cached device status
        """
        return self._device_status_cache.copy()
    
    def clear_status_cache(self) -> int:
        """Clear status cache

        Returns:
            int: Number of cleared cache items
        """
        cache_count = len(self._device_status_cache)
        self._device_status_cache.clear()
        self._last_status_update = None
        _LOGGER.info(f"Cleared {cache_count} device status caches")
        return cache_count
    
    @property
    def last_status_update(self) -> Optional[datetime]:
        """Last status update time"""
        return self._last_status_update