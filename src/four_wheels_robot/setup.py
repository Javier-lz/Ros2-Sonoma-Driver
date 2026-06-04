from setuptools import find_packages, setup
import os 
from glob import glob

package_name = 'four_wheels_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
        (os.path.join('share',package_name,'models/prius_hybrid'),glob('models/prius_hybrid/*'))
    ],

    zip_safe=True,
    maintainer='javierlz',
    maintainer_email='javierlazaromanzanas@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',

   
)

