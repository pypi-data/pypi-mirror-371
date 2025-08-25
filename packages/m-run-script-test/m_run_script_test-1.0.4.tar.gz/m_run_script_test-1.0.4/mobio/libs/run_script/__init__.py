import datetime
import json
import os
import re
import subprocess
from copy import deepcopy
from functools import wraps
from pathlib import Path

import requests
import time

from .slack_helper import SlackHelper

__all__ = ["MobioRunScript"]


class ParamConfig:
    data_dir = "data_dir"
    image_version = "image.version"
    file_script_result = "init_script.result"
    first_deploy = "first_deploy"
    script = "script"
    version_exclude = "version_exclude"
    run_all_version = "run_all_version"
    every_deploy = "every_deploy"
    version = "version"
    script_executed = "script_executed"
    status_success = "status_success"
    version_success = "version_success"
    version_not_required = "version_not_required"
    success = "success"
    pending = "pending"
    yes = 1
    no = 0
    host_name = os.environ.get("HOSTNAME")
    logs_dir = "APPLICATION_LOGS_DIR"
    logs_name = "{}_init_script.log"
    folder_handshake = 'run_script_cross_module'


class PathFile:
    DATA_DIR = os.environ.get(ParamConfig.data_dir)
    FILE_SCRIPT_RESULT = os.path.join(DATA_DIR, ParamConfig.file_script_result)
    IMAGE_VERSION = os.path.join(DATA_DIR, ParamConfig.image_version)
    KUBERNETES_TOKEN = "/run/secrets/kubernetes.io/serviceaccount/token"
    PATH_SHARE_DATA = os.path.dirname(DATA_DIR)
    FOLDER_HANDSHAKE = os.path.join(PATH_SHARE_DATA, ParamConfig.folder_handshake)
    LOG_SCRIPT_RUN = os.environ.get(ParamConfig.logs_dir)


class MobioRunScript:

    @classmethod
    def save_data_to_file(cls, file_path, data):
        print("save_data_to_file file_path: {}".format(file_path))
        print("save_data_to_file file_data: {}".format(data))
        i = 0
        while True:
            try:
                if i >= 10:
                    break
                Path(os.path.dirname(os.path.abspath(file_path))).mkdir(
                    parents=True, exist_ok=True
                )
                with open(file_path, "w") as fout:
                    fout.write(data)
                    fout.close()
                break
            except IOError as ex:
                print("utils::save_data_to_file():message: %s" % ex)
                time.sleep(0.1)
                i += 1
        print("save_data_to_file file_path: {} - SUCCESS".format(file_path))

    @classmethod
    def get_content_from_file(cls, file_path):
        content_file = None
        if not os.path.exists(file_path):
            return content_file
        i = 0
        while True:
            try:
                if i >= 10:
                    break
                with open(file_path, "r") as fout:
                    content_file = fout.read().replace("\r", "").replace("\n", "")
                    fout.close()
                break
            except IOError as ex:
                print("utils::get_content_from_file():message: %s" % ex)
                time.sleep(0.1)
                i += 1
        return content_file

    @classmethod
    def get_json_script_result(cls):
        result = {}
        try:
            content = cls.get_content_from_file(PathFile.FILE_SCRIPT_RESULT)
            if content:
                result = json.loads(content)
        except Exception as err:
            print("get_json_script_result err: {}".format(err))
        print("get_json_script_result result: {}".format(result))
        return result

    @classmethod
    def call_script(cls, command):
        try:
            print("call_script begin command: {}".format(command))
            result = subprocess.run(["/bin/bash", "-c", command])
            print("call_script end command: {}".format(command))
            return result.returncode
        except Exception as err:
            print("call_script err: {}".format(err))
            cls.log_info(content="Exception {}: {}".format(command, err), lv_log=2)
            return 1

    @classmethod
    def save_result_script(cls, json_result):
        data_file = json.dumps(json_result)
        cls.save_data_to_file(PathFile.FILE_SCRIPT_RESULT, data_file)

    @classmethod
    def save_result_init_container(cls, value):
        # save_data_to_file(PathFile.FILE_CONTAINER_RESULT, value)
        # if value == ParamConfig.success:
        #     image_name = cls.get_name_image_version()
        #     cls.save_data_to_file(PathFile.IMAGE_VERSION, image_name)
        pass

    @classmethod
    def run_script_has_first_deploy(cls, script_config):
        """
        :param script_config:
            {
                "first_deploy": {
                    "script": [],
                    "version_exclude": [],
                    "run_all_version": 0
                },
                "every_deploy": {
                    "script": [
                        "PYTHONPATH=./ python3.8 -u sync_mongodb_index.py",
                        "PYTHONPATH=./ python3.8 -u sync_kafka_topic.py"
                    ]
                },
                "version": {
                }
            }
        :return:
        """
        try:
            # script_result:
            # {
            # 	"first_deploy": {
            #       "script_executed": [],
            #       "status_success": 1/0
            # 	},
            # 	"every_deploy": {
            # 		"script_executed": ["PYTHONPATH=./ python3.8 -u sync_kafka_topic.py",
            # 		"PYTHONPATH=./ python3.8 -u sync_mongodb_index.py"]
            # 	},
            # 	"version": {
            # 		"1": ["PYTHONPATH=./ python3.8 -u scripts/script_init_database.py"],
            # 		"2": ["PYTHONPATH=./ python3.8 -u scripts/script_init_database.py"]
            # 	}
            # }
            # save_result_init_container(value=ParamConfig.pending)
            script_result = cls.get_json_script_result()
            first_deploy = False
            if ParamConfig.first_deploy not in script_result:
                script_result[ParamConfig.first_deploy] = {}
            if ParamConfig.every_deploy not in script_result:
                script_result[ParamConfig.every_deploy] = {}
            if ParamConfig.version not in script_result:
                script_result[ParamConfig.version] = {}
            if script_result.get(ParamConfig.first_deploy, {}).get(ParamConfig.status_success,
                                                                   ParamConfig.no) == ParamConfig.no:
                script_executed = script_result.get(
                    ParamConfig.first_deploy, {}).get(ParamConfig.script_executed, [])
                first_deploy_script = script_config.get(
                    ParamConfig.first_deploy, {}).get(ParamConfig.script, [])
                if not first_deploy_script:
                    script_result.get(ParamConfig.first_deploy, {})[
                        ParamConfig.status_success] = ParamConfig.yes
                else:
                    first_deploy_script_need_run = list(
                        set(first_deploy_script) - set(script_executed))
                    print("run_script first_deploy_script_need_run: {}".format(
                        first_deploy_script_need_run))
                    for script_run in first_deploy_script_need_run:
                        if cls.call_script(script_run) != 0:  # call fail
                            return cls.save_result_script(script_result)
                        script_executed.append(script_run)
                        script_result.get(ParamConfig.first_deploy, {})[
                            ParamConfig.script_executed] = script_executed
                first_deploy = True

            print("run_script script_result first_deploy: {}".format(script_result))
            every_deploy_script = list(set(script_config.get(
                ParamConfig.every_deploy, {}).get(ParamConfig.script, [])))
            print("run_script every_deploy_script: {}".format(every_deploy_script))
            for script_run in every_deploy_script:
                if cls.call_script(script_run) != 0:
                    return cls.save_result_script(script_result)
            script_result.get(ParamConfig.every_deploy, {})[ParamConfig.script_executed] = every_deploy_script
            print("run_script script_result every_deploy: {}".format(script_result))

            script_config[ParamConfig.version] = {
                int(k): v for k, v in script_config.get(ParamConfig.version, {}).items()
            }
            script_result[ParamConfig.version] = {
                int(k): v for k, v in script_result.get(ParamConfig.version, {}).items()
            }
            list_version = list(script_config.get(
                ParamConfig.version, {}).keys())
            list_version.sort()
            list_version_result = list(
                script_result.get(ParamConfig.version, {}).keys())
            list_version_result.sort()
            last_version = list_version_result[-1] if list_version_result else None
            if last_version and last_version in list_version:
                # lay script cuoi lan trc chay de dam bao da chay du
                index_last = list_version.index(last_version)
                list_version = list_version[index_last:]
            print("run_script list_version: {}".format(list_version))
            if first_deploy:
                print("run_script first_deploy True")
                if script_config.get(ParamConfig.first_deploy, {}).get(ParamConfig.run_all_version) == ParamConfig.yes:
                    version_exclude = script_config.get(ParamConfig.first_deploy, {}).get(
                        ParamConfig.version_exclude, [])
                    for version in list_version:
                        if version not in version_exclude:
                            list_script_old = script_result.get(ParamConfig.version, {}).get(version, [])
                            list_script_new = script_config.get(ParamConfig.version, {}).get(version, [])
                            first_script_need_run = list(
                                set(list_script_new) - set(list_script_old))
                            print("run_script version: {} list script: {}".format(
                                version, first_script_need_run))
                            for script_run in first_script_need_run:
                                if cls.call_script(script_run) != 0:  # call fail
                                    return cls.save_result_script(script_result)
                                list_script_old.append(script_run)
                                script_result.get(ParamConfig.version, {})[
                                    version] = list_script_old
                else:
                    if list_version:
                        # luu lai version cuoi de lan sau chay tu script sau
                        script_result.get(ParamConfig.version, {})[list_version[-1]] = script_config.get(
                            ParamConfig.version, {}).get(list_version[-1], [])
                script_result.get(ParamConfig.first_deploy, {})[
                    ParamConfig.status_success] = ParamConfig.yes
            # co van de khi deploy lan dau chay first deploy nhung lai ko chay script version
            else:
                print("run_script first_deploy False")
                for version in list_version:
                    list_script_old = script_result.get(
                        ParamConfig.version, {}).get(version, [])
                    list_script_new = script_config.get(
                        ParamConfig.version, {}).get(version, [])
                    first_script_need_run = list(
                        set(list_script_new) - set(list_script_old))
                    print("run_script version: {} list script: {}".format(
                        version, first_script_need_run))
                    for script_run in first_script_need_run:
                        if cls.call_script(script_run) != 0:  # call fail
                            return cls.save_result_script(script_result)
                        list_script_old.append(script_run)
                        script_result.get(ParamConfig.version, {})[
                            version] = list_script_old
            print("run_script script_result version: {}".format(script_result))
            cls.save_result_script(script_result)
            cls.save_result_init_container(value=ParamConfig.success)
        except Exception as err:
            print("run_script err: {}".format(err))

    @classmethod
    def run_script_by_version(cls, script_config):
        """
        :param script_config:
            {
                "first_deploy": {
                    "script": [],
                    "version_exclude": [],
                    "run_all_version": 0
                },
                "every_deploy": {
                    "script": [
                        "PYTHONPATH=./ python3.8 -u sync_mongodb_index.py",
                        "PYTHONPATH=./ python3.8 -u sync_kafka_topic.py"
                    ]
                },
                "version": {
                }
            }
        :return:
        """

        # script_result:
        # {
        # 	"first_deploy": {
        #       "script_executed": [],
        #       "status_success": 1/0
        # 	},
        # 	"every_deploy": {
        # 		"script_executed": ["PYTHONPATH=./ python3.8 -u sync_kafka_topic.py",
        # 		"PYTHONPATH=./ python3.8 -u sync_mongodb_index.py"]
        # 	},
        # 	"version": {
        # 		"1": ["PYTHONPATH=./ python3.8 -u scripts/script_init_database.py"],
        # 		"2": ["PYTHONPATH=./ python3.8 -u scripts/script_init_database.py"]
        # 	}
        # }
        script_result = cls.get_json_script_result()
        if ParamConfig.every_deploy not in script_result:
            script_result[ParamConfig.every_deploy] = {}
        if ParamConfig.version not in script_result:
            script_result[ParamConfig.version] = {}

        every_deploy_script = script_config.get(
            ParamConfig.every_deploy, {}).get(ParamConfig.script, [])
        print("run_script every_deploy_script: {}".format(every_deploy_script))
        for script_run in every_deploy_script:
            if cls.call_script(script_run) != 0:
                cls.raise_error_run_script(script_run)
        script_result.get(ParamConfig.every_deploy, {})[ParamConfig.script_executed] = every_deploy_script
        print("run_script script_result every_deploy: {}".format(script_result))

        script_config[ParamConfig.version] = {
            int(k): v for k, v in script_config.get(ParamConfig.version, {}).items()
        }
        script_result[ParamConfig.version] = {
            int(k): v for k, v in script_result.get(ParamConfig.version, {}).items()
        }
        list_version = list(script_config.get(ParamConfig.version, {}).keys())
        list_version.sort()
        list_version_result = list(
            script_result.get(ParamConfig.version, {}).keys())
        list_version_result.sort()
        last_version = list_version_result[-1] if list_version_result else None
        if last_version and last_version in list_version:
            # lay script cuoi lan trc chay de dam bao da chay du
            index_last = list_version.index(last_version)
            list_version = list_version[index_last:]
        print("run_script list_version: {}".format(list_version))

        for version in list_version:
            list_script_old = script_result.get(ParamConfig.version, {}).get(version, [])
            list_script_new = script_config.get(ParamConfig.version, {}).get(version, [])
            print("run_script version: {} list script: {}".format(
                version, list_script_new))
            script_need_run = list(set(list_script_new) - set(list_script_old))
            if script_need_run:
                cls.log_info(content="======================= Version {} START ============".format(
                    version), lv_log=0)
            # phai chay for list_script_new ma ko for script_need_run vi can chay dung thu tu, script_need_run co the da bi thay doi thu tu
            for idx, script_run in enumerate(list_script_new):
                idx_script = idx + 1
                if script_run in list_script_old:
                    print("{} has run".format(script_run))
                    continue
                cls.log_info(content="{}. {} START".format(idx_script, script_run), lv_log=1)
                if cls.call_script(script_run) != 0:  # call fail
                    cls.save_result_script(script_result)
                    cls.raise_error_run_script(script_run)
                list_script_old.append(script_run)
                script_result.get(ParamConfig.version, {})[
                    version] = list_script_old
                cls.log_info(content="{}. {} END".format(idx_script, script_run), lv_log=1)
            if script_need_run:
                cls.log_info(content="======================= Version {} END ============".format(
                    version), lv_log=0)
        print("run_script script_result: {}".format(script_result))
        cls.save_result_script(script_result)
        cls.save_result_init_container(value=ParamConfig.success)

    @classmethod
    def raise_error_run_script(cls, script_run):
        raise ValueError("{} RUN FAIL".format(script_run))

    # def check_result_run_script():
    #     time.sleep(10)
    #     print("check_result_run_script file: {}".format(PathFile.FILE_CONTAINER_RESULT))
    #     content = get_content_from_file(PathFile.FILE_CONTAINER_RESULT)
    #     print("check_result_run_script content: {}".format(content))
    #     while True:
    #         if content and content == "success":
    #             break
    #         print("check_result_run_script sleep 3s")
    #         time.sleep(3)
    #         content = get_content_from_file(PathFile.FILE_CONTAINER_RESULT)
    #         print("check_result_run_script content: {}".format(content))
    #     print("check_result_run_script END")

    @classmethod
    def check_result_run_script(cls):
        # time.sleep(10)
        print("check_result_run_script file: {}".format(PathFile.IMAGE_VERSION))
        content = cls.get_content_from_file(PathFile.IMAGE_VERSION)
        print("check_result_run_script content: {}".format(content))
        image_name = cls.get_name_image_version()
        while True:
            if content and content == image_name:
                break
            print("check_result_run_script sleep 3s")
            time.sleep(3)
            content = cls.get_content_from_file(PathFile.IMAGE_VERSION)
            print("check_result_run_script content: {}".format(content))
        print("check_result_run_script END")

    @classmethod
    def get_name_image_version(cls):
        url = "https://kubernetes.default.svc/api/v1/namespaces/mobio/pods/{HOSTNAME}".format(
            HOSTNAME=ParamConfig.host_name)
        content = cls.get_content_from_file(PathFile.KUBERNETES_TOKEN)
        headers = {
            'Authorization': 'Bearer {}'.format(content),
        }
        data_res = requests.get(
            url,
            headers=headers,
            verify=False,
            timeout=10
        )
        data_json = data_res.json()
        image_name = data_json.get("status", {}).get(
            "containerStatuses", [])[0].get("image")
        print("get_name_image_version image_name: {}".format(image_name))
        return image_name

    @classmethod
    def run_script_not_required(cls, script_config):
        """
        :param script_config:
            {
                "first_deploy": {
                    "script": [],
                    "version_exclude": [],
                    "run_all_version": 0
                },
                "every_deploy": {
                    "script": [
                        "PYTHONPATH=./ python3.8 -u sync_mongodb_index.py",
                        "PYTHONPATH=./ python3.8 -u sync_kafka_topic.py"
                    ]
                },
                "version": {
                }
            }
        :return:
        """

        # script_result:
        # {
        # 	"first_deploy": {
        #       "script_executed": [],
        #       "status_success": 1/0
        # 	},
        # 	"every_deploy": {
        # 		"script_executed": ["PYTHONPATH=./ python3.8 -u sync_kafka_topic.py",
        # 		"PYTHONPATH=./ python3.8 -u sync_mongodb_index.py"]
        # 	},
        # 	"version": {
        # 		"1": ["PYTHONPATH=./ python3.8 -u scripts/script_init_database.py"],
        # 		"2": ["PYTHONPATH=./ python3.8 -u scripts/script_init_database.py"]
        # 	}
        # }
        script_result = cls.get_json_script_result()
        if ParamConfig.every_deploy not in script_result:
            script_result[ParamConfig.every_deploy] = {}
        if ParamConfig.version not in script_result:
            script_result[ParamConfig.version] = {}
        if ParamConfig.version_not_required not in script_result:
            script_result[ParamConfig.version_not_required] = {}

        script_config[ParamConfig.version_not_required] = {
            int(k): v for k, v in script_config.get(ParamConfig.version_not_required, {}).items()
        }
        script_result[ParamConfig.version_not_required] = {
            int(k): v for k, v in script_result.get(ParamConfig.version_not_required, {}).items()
        }
        list_version = list(script_config.get(
            ParamConfig.version_not_required, {}).keys())
        list_version.sort()
        list_version_result = list(script_result.get(
            ParamConfig.version_not_required, {}).keys())
        list_version_result.sort()
        last_version = list_version_result[-1] if list_version_result else None
        if last_version and last_version in list_version:
            # lay script cuoi lan trc chay de dam bao da chay du
            index_last = list_version.index(last_version)
            list_version = list_version[index_last:]
        print("run_script list_version: {}".format(list_version))

        for version in list_version:
            list_script_old = script_result.get(ParamConfig.version_not_required, {}).get(version, [])
            list_script_new = script_config.get(ParamConfig.version_not_required, {}).get(version, [])
            print("run_script version: {} list script: {}".format(
                version, list_script_new))
            script_need_run = list(set(list_script_new) - set(list_script_old))
            if script_need_run:
                cls.log_info(content="======================= Version not required {} START ============".format(
                    version), lv_log=0)
            for idx, script_run in enumerate(list_script_new):
                idx_script = idx + 1
                if script_run in list_script_old:
                    print("{} has run".format(script_run))
                    continue
                cls.log_info(content="{}. {} START".format(idx_script, script_run), lv_log=1)
                if cls.call_script(script_run) != 0:  # call fail
                    cls.save_result_script(script_result)
                    cls.raise_error_run_script(script_run)
                list_script_old.append(script_run)
                script_result.get(ParamConfig.version_not_required, {})[
                    version] = list_script_old
                cls.log_info(content="{}. {} END".format(idx_script, script_run), lv_log=1)
            if script_need_run:
                cls.log_info(content="======================= Version not required {} END ============".format(
                    version), lv_log=0)
        print("run_script script_result: {}".format(script_result))
        cls.save_result_script(script_result)

    @staticmethod
    def get_module_run_script():
        data_dir = PathFile.DATA_DIR
        module_name = data_dir.split("/")[-1]
        return module_name.strip("/")

    @classmethod
    def build_path_save_log(cls):
        module_name = cls.get_module_run_script()
        file_log_name = deepcopy(ParamConfig.logs_name).format(module_name)
        path_file_log = os.path.join(PathFile.LOG_SCRIPT_RUN, file_log_name)
        return path_file_log

    @classmethod
    def build_text_log(cls, text_log, lv_log=2):
        log_format = "{} {}: {}\n"
        utc_now = cls.get_utc_now()
        date_format = utc_now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if lv_log == 0:
            return log_format.format("*", date_format, text_log)
        elif lv_log == 1:
            return log_format.format("\t" * lv_log + "-", date_format, text_log)
        else:
            return log_format.format("\t" * lv_log + "+", date_format, text_log)

    @classmethod
    def log_info(cls, content, lv_log=2):
        print(cls.build_text_log(content, lv_log=lv_log))
        # path_file_log = cls.build_path_save_log()
        # with open(path_file_log, "a", encoding="utf-8") as file:
        #     file.write(cls.build_text_log(content, lv_log=lv_log))
        #     file.close()

    @staticmethod
    def send_alert_slack(content, slack_uri=None, title=None, author_name=None, pretext=None, success=True):
        return SlackHelper(slack_uri).send_alert(
            content, title=title, author_name=author_name, pretext=pretext, success=success)

    @staticmethod
    def get_utc_now():
        return datetime.datetime.now(datetime.UTC)

    @staticmethod
    def validate_key_input(key):
        pattern = r'^[a-zA-Z0-9_]+$'
        if not re.fullmatch(pattern, key):
            raise ValueError('validate_key_input::key must only contain a-z, A-Z, 0-9 and _')

    @classmethod
    def start_script_cross_module(cls, key):
        def deco_function(f):
            @wraps(f)
            def f_start(*args, **kwargs):
                # Validate key
                print("*** start_script_cross_module:: Validate key ***")
                cls.validate_key_input(key)
                file_handshake = key

                # Tạo thư mục chứa file handshake nếu chưa tồn tại
                print(
                    "*** start_script_cross_module:: Create folder handshake if not exist ***")
                path_file_handshake = os.path.join(
                    PathFile.FOLDER_HANDSHAKE, file_handshake)
                Path(os.path.dirname(os.path.abspath(path_file_handshake))).mkdir(
                    parents=True, exist_ok=True
                )
                file_handshake_obj = Path(path_file_handshake)

                # Xoá file handshake nếu đã tồn tại
                print("*** start_script_cross_module:: Delete file handshake if exist ***")
                if file_handshake_obj.exists():  # Kiểm tra nếu tệp tồn tại
                    file_handshake_obj.unlink()  # Xóa tệp

                # Bắt đầu chạy script
                print("*** start_script_cross_module:: Start script cross module ***")
                f(*args, **kwargs)

                # Ghi file handshake
                print("*** start_script_cross_module:: Write key handshake ***")
                i = 0
                while True:
                    try:
                        if i >= 10:
                            break
                        file_handshake_obj.touch()
                        break
                    except IOError as ex:
                        print("start_script_cross_module::ERROR IOError: %s" % ex)
                        time.sleep(0.1)
                        i += 1
                print(
                    "*** start_script_cross_module:: SUCCESS - file_path: {}".format(path_file_handshake))

            return f_start  # true decorator

        return deco_function

    @classmethod
    def end_script_cross_module(cls, key):
        def deco_function(f):
            @wraps(f)
            def f_end(*args, **kwargs):
                # Validate key
                print("*** end_script_cross_module:: Validate key ***")
                cls.validate_key_input(key)
                file_handshake = key

                # Tạo thư mục chứa file handshake nếu chưa tồn tại
                print(
                    "*** end_script_cross_module:: Create folder handshake if not exist ***")
                path_file_handshake = os.path.join(
                    PathFile.FOLDER_HANDSHAKE, file_handshake)
                Path(os.path.dirname(os.path.abspath(path_file_handshake))).mkdir(
                    parents=True, exist_ok=True
                )
                file_handshake_obj = Path(path_file_handshake)

                # Đợi cho đến khi tìm thấy file handshake
                t1 = cls.get_utc_now()
                while True:
                    if file_handshake_obj.exists():
                        break
                    time.sleep(1)
                    t2 = cls.get_utc_now()
                    print(
                        "*** end_script_cross_module:: Wait file handshake - wait time: {} ***".format(t2 - t1))

                # Bắt đầu chạy script
                print("*** end_script_cross_module:: Start script cross module ***")
                f(*args, **kwargs)

                # Xoá file handshake
                print("*** end_script_cross_module:: Delete file handshake ***")
                i = 0
                while True:
                    try:
                        if i >= 10:
                            break
                        if file_handshake_obj.exists():  # Kiểm tra nếu tệp tồn tại
                            file_handshake_obj.unlink()  # Xóa tệp
                        break
                    except IOError as ex:
                        print("end_script_cross_module::ERROR IOError: %s" % ex)
                        time.sleep(0.1)
                        i += 1
                print(
                    "*** end_script_cross_module:: SUCCESS - file_path: {}".format(path_file_handshake))

            return f_end  # true decorator

        return deco_function


if __name__ == '__main__':
    MobioRunScript.log_info(content="======================= Version not required {} START ============".format(
        1), lv_log=0)
    MobioRunScript.log_info(
        content="{}. {} START".format(1, "script_run"), lv_log=1)
    MobioRunScript.log_info(content="hello", lv_log=2)
    MobioRunScript.log_info(
        content="co loi xay ra vui long lien he admin", lv_log=2)
    MobioRunScript.log_info(
        content="{}. {} END".format(1, "script_run"), lv_log=1)
    MobioRunScript.log_info(content="======================= Version not required {} END ============".format(
        1), lv_log=0)
