#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os

import yaml

from rainbow.build.image.image_builder import ImageBuilder, ServiceImageBuilderMixin
from rainbow.core.util import files_util, class_util


def build_rainbows(path):
    """
    TODO: doc for build_rainbows
    """
    config_files = files_util.find_config_files(path)

    for config_file in config_files:
        print(f'Building artifacts for file: {config_file}')

        base_path = os.path.dirname(config_file)

        with open(config_file) as stream:
            rainbow_config = yaml.safe_load(stream)

            for pipeline in rainbow_config['pipelines']:
                for task in pipeline['tasks']:
                    task_type = task['type']
                    builder_class = __get_task_build_class(task_type)
                    if builder_class:
                        __build_image(base_path, task, builder_class)
                    else:
                        raise ValueError(f'No such task type: {task_type}')

                for service in rainbow_config['services']:
                    service_type = service['type']
                    builder_class = __get_service_build_class(service_type)
                    if builder_class:
                        __build_image(base_path, service, builder_class)
                    else:
                        raise ValueError(f'No such service type: {service_type}')


def __build_image(base_path, builder_config, builder):
    if 'source' in builder_config:
        builder_instance = builder(
            config=builder_config,
            base_path=base_path,
            relative_source_path=builder_config['source'],
            tag=builder_config['image'])
        builder_instance.build()
    else:
        print(f"No source provided for {builder_config['name']}, skipping.")


def __get_task_build_class(task_type):
    return task_build_classes[task_type] if task_type in task_build_classes else None


def __get_service_build_class(service_type):
    return service_build_classes[service_type] if service_type in service_build_classes else None


print(f'Loading image builder implementations..')

# TODO: add configuration for user image builders package
image_builders_package = 'rainbow/build/image'
user_image_builders_package = 'TODO: user_image_builders_package'

task_build_classes = class_util.find_subclasses_in_packages(
    [image_builders_package, user_image_builders_package],
    ImageBuilder)

print(f'Finished loading image builder implementations: {task_build_classes}')

print(f'Loading service image builder implementations..')

# TODO: add configuration for user service image builders package
service_builders_package = 'rainbow/build/service'
user_service_builders_package = 'TODO: user_service_builders_package'

service_build_classes = class_util.find_subclasses_in_packages(
    [service_builders_package, user_service_builders_package],
    ServiceImageBuilderMixin)

print(f'Finished loading service image builder implementations: {service_build_classes}')
