import socket
from typing import Optional
from loguru import logger   
from qlsdk.rsc.network.discover import UdpBroadcaster
from threading import Thread
from qlsdk.core import *
from qlsdk.rsc.device import QLBaseDevice, DeviceFactory
from qlsdk.rsc.interface import IDevice
from qlsdk.rsc.proxy import DeviceProxy
import time
        
        
class DeviceContainer(object):
    def __init__(self, proxy_enabled=False, tcp_port = 19216):
        self._devices = {}
        self._tcp_port = tcp_port
        self._proxy_enabled = proxy_enabled
        
        # 设备搜索广播器
        self._broadcaster = UdpBroadcaster()
        self._broadcaster.start()
        
        # 监听设备连接
        self._listening_thread = Thread(target=self._listening)
        self._listening_thread.daemon = True
        self._listening_thread.start()
        
    @property
    def devices(self)-> IDevice:
        return self._devices
    
    '''
        等待设备连接
    '''
    def connect(self, device_id: str, timeout:int=30) -> Optional[IDevice]:        
        logger.info(f"开始搜索设备: {device_id}")
        self.add_search(device_id)
        for s in range(timeout):
            device = self.get_device(device_id)
            if device:
                logger.success(f"设备[{device_id}]已连接成功。")
                return device
            time.sleep(1)
        logger.warning(f"在{timeout}内未搜索到设备：{device_id}")
        return None
            
    def _listening(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            # 绑定到所有接口的19216端口
            tcp_socket.bind(('0.0.0.0', self._tcp_port))
            tcp_socket.listen(100)
            logger.info(f"端口[{self._tcp_port}]监听服务已启动")

            while True:
                client_socket, addr = tcp_socket.accept()
                logger.info(f"接收到来自[{addr[0]}:{addr[1]}]的连接，待确认设备类型...")
                
                
                # 为每个新连接创建线程处理
                try:
                    client_handler = Thread(
                        target=self.client_handler,
                        args=(client_socket,),
                        daemon=False
                    )
                    
                    client_handler.start()
                except Exception as e:
                    logger.error(f"Handler Error: {e}")
                
        except KeyboardInterrupt:
            logger.error(f"端口[{self._tcp_port}]监听服务异常关闭")
        except Exception as e:
            logger.error(f"端口[{self._tcp_port}]监听服务异常: {e}")
        finally:
            logger.error(f"端口[{self._tcp_port}]监听服务关闭")
            tcp_socket.close()
            
    def client_handler(self, client_socket):
                
        if self._proxy_enabled:
            # 启动代理  TODO: 代理的同时支持接口控制和数据转发
            proxy = DeviceProxy(client_socket)
            proxy.start()
        else:            
            # 数据监听
            device = QLBaseDevice(client_socket)
            device.start_listening()
            # GET_DEVICE_INFO
            msg = GetDeviceInfoCommand.build(device).pack()
            logger.trace(f"发送获取设备信息命令: {msg.hex()}")
            device.send(msg)
            # 添加设备
            while True:
                if device.device_name:
                    real_device = DeviceFactory.create_device(device)
                    device.stop_listening()
                    real_device.start_listening()
                    self.add_device(real_device)
                    logger.info(f"设备[{device.device_name}]已连接，设备类型为：{hex(real_device.device_type)}")
                    break
            
        
    # 搜寻设备
    def add_search(self, device_id):
        self._broadcaster.add_device(device_id)
        
    def add_device(self, device: IDevice):
        if device is None or device.device_no is None:
            logger.warning("无效的设备")
            
        self._devices[device.device_no] = device
        logger.info(f"添加设备[{device.device_no}]到设备列表，已连接设备数量：{len(self._devices)}")
        
        # 标记设备为已连接
        self._broadcaster.mark_device_as_connected(device.device_no)
        
    def get_device(self, device_no:str=None)->IDevice:
        logger.info(f"已连接设备数量:{len(self._devices)}")
        if len(self._devices) == 0:
            return None
        
        # 未指定device_id，返回第一个设备
        if device_no is None:
            return list(self._devices.values())[0]
        
        return self._devices.get(device_no, None)
            