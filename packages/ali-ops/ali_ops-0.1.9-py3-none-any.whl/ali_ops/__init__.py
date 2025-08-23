

import fire 
import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from config import CONFIG
from vpc import VPC 
from ecs import ECS 


class ENTRY(object):
    """主入口类"""
    
    def __init__(self):
        # 使用装饰器创建VPC访问控制代理
        self.vpc = VPC
        self.ecs = ECS
        self.config = CONFIG() 
    

def main() -> None:
    """Main function to run the CLI."""
    fire.Fire(ENTRY)

