from setuptools import find_packages, setup
import os 
from glob import glob

package_name = 'four_wheels_robot_nn'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'models'), glob('models/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*'))
    ],
    install_requires=['setuptools',
                      'ultralytics',
                      'numpy<2.0.0'],
    zip_safe=True,
    maintainer='javierlz',
    maintainer_email='javierlazaromanzanas@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'processorimg = four_wheels_robot_nn.image_processing:main',
            'training_node = four_wheels_robot_nn.training:main',
            'datagathering = four_wheels_robot_nn.data_gather_node:main'
        ],
    },
)

