import os
import pathlib
import time
import json
import signal
import sys
from loguru import logger
from datetime import datetime

# import prettytable as pt
from textwrap import fill
from ctypes import *


def get_cmd_str(password, cmd_str):
    ip_str = "2.160"
    if ip_str != "":
        cmd = "sshpass -p  '%s' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@192.168.%s exec '%s'" % (password, ip_str, cmd_str)
        return cmd
    else:
        print("无配置文件，无法获取sensor_hubip")
        exit()


def get_camera_register_info(info_list, register_idx):
    camera_register_list = []
    for idx, info in enumerate(info_list):
        if register_idx in info:
            for i in range(3):
                register_info_list = info_list[idx + i].strip().split("\t")[-1].strip().split(" ")
                for register_info in register_info_list:
                    camera_register_list.append(register_info)

    return camera_register_list


def get_camera_register_image_info(info_list, register_idx):
    camera_register_list = []
    for idx, info in enumerate(info_list):
        if register_idx in info:
            for i in range(4):
                register_info_list = info_list[idx + i].strip().split("\t")[-1].strip().split(" ")
                for register_info in register_info_list:
                    camera_register_list.append(register_info)

    return camera_register_list


def get_b_str(hex_str, bit_num):
    int_hex = int(hex_str, 16)
    bit_str = ""
    if int(bit_num) == 16:
        bit_str = '{:016b}'.format(int_hex)
    if int(bit_num) == 32:
        bit_str = '{:032b}'.format(int_hex)
    return bit_str


def get_float_num(num):
    # 转为10进制
    i = int(num, 16)
    # 转为c integer
    cp = pointer(c_int(i))
    # 将int pointer转为float pointer
    fp = cast(cp, POINTER(c_float))
    return fp.contents.value


def sh2_check(config_file, log_file_name, vehicle_type, cam_list, loop_time, dt_str, sh_dict):
    password = "root"
    vsync_dict = {}
    if vehicle_type == "mkz":
        check_cam_dict = {'10': 'U60', '12': 'F197', '13': 'R197', '14': 'Rear197', '15': 'L197', '4': 'F30',
                    '5': 'F120', '6': 'LF100', '7': 'RF100', '8': 'LR60', '9': 'RR60'}
    else:
        check_cam_dict = {'10': 'U60', '11': 'D60', '12': 'F197', '13': 'R197', '14': 'Rear197', '15': 'L197', '4': 'F30',
                    '5': 'F120', '6': 'LF100', '7': 'RF100', '8': 'LR60', '9': 'RR60'}
    if len(cam_list) == 0:
        print("检查所有相机")
        vsync_dict = check_cam_dict
    else:
        for i in cam_list:
            i = str(i)
            vsync_dict[i] = check_cam_dict[i]
    print("检查的相机为:")
    print(vsync_dict)
    sensorhub_status_flag = True
    sensorhub_camera_dick = {}
    for i in vsync_dict:
        sensorhub_camera_dick["--当前检测时间为"] = dt_str
        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict[i])] = {}
        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict[i])]["--分隔符"] = "======================================"
        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict[i])]["--sensorhub_status"] = True
    # sensorhub开机自检的相机状态
    # try:
    #     cmd_str = 'mem-test r 0x80020000 10 4'
    #     cmd = get_cmd_str(password, cmd_str)
    #     info_list = os.popen(cmd).readlines()
    #     for info in info_list:
    #         if "0x00000010" in info:
    #             result_list = []
    #             # result_list.append(info.strip().replace("\r", "").replace("\n", ""))
    #             isp_str = str(info.strip().split(" ")[-3].strip()[-4:])
    #             isp_int = int(isp_str, 16)
    #             isp_b = '{:016b}'.format(isp_int)
    #             isp_b_result = isp_b[:-4][::-1]
    #             flag_0x = True
    #             for idx, vsync in enumerate(isp_b_result):
    #                 if "0" in vsync:
    #                     pass
    #                 else:
    #                     result_list.append("相机%s，%s 的开机自检版本读取有问题" % (str(idx + 4), vsync_dict[str(idx + 4)]))
    #                     flag_0x = False
    #             if flag_0x:
    #                 sensorhub_camera_dick["sensorhub开机自检的相机状态"] = "所有相机开机自检正常"
    #             else:
    #                 sensorhub_camera_dick["sensorhub开机自检的相机状态"] = result_list
    # except Exception as e:
    #     sensorhub_camera_dick["sensorhub开机自检的相机状态"] = str(e)

    # 杀掉isp_monitor进程
    try:
        cmd_str = 'ps -ef | grep isp_monitor | grep -v grep'
        cmd = get_cmd_str(password, cmd_str)
        info_list = os.popen(cmd).readlines()
        print("检查isp_monitor是否打开")
        for info in info_list:
            if "grep isp_monitor" not in info:
                cmd_str = 'kill -9 %s' % info.strip().split(" ")[0]
                cmd = get_cmd_str(password, cmd_str)
                info_list = os.popen(cmd).readlines()
                print("isp_monitor关闭成功")
            else:
                pass
    except Exception as e:
        sensorhub_camera_dick["杀掉isp_monitor进程"] = e
    # 检查ISP上电状态
    power_num = 0
    try:
        print("检查ISP上电状态")
        while True:
            cmd_str = 'mem-test r 0x80000000 20 1'
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            isp_power_flag = True
            for info in info_list:
                if "0x00000020" in info:
                    channel_info_str_power = str(info.strip().split("\t")[-1].strip().split(" ")[0][-4:])
                    result_list_power = []
                    channel_info_int_power = int(channel_info_str_power, 16)
                    channel_info_b_power = '{:016b}'.format(channel_info_int_power)
                    channel_info_b_result_power = channel_info_b_power[:-4][::-1]
                    for idx, idx_info in enumerate(channel_info_b_result_power):
                        if str(idx + 4) in vsync_dict.keys():
                            if "1" in idx_info:
                                result_list_power.append(
                                    "相机%s，%s 的相机处于%s" % (str(idx + 4), vsync_dict[str(idx + 4)], "上电状态"))
                            else:
                                result_list_power.append(
                                    "\033[0;31m 相机%s，%s 的相机处于%s \033[0m" % (str(idx + 4), vsync_dict[str(idx + 4)], "断电状态"))
                                isp_power_flag = False
                    if isp_power_flag:
                        sensorhub_camera_dick["00检查ISP上电状态"] = result_list_power
                        print("--------------")
                    else:
                        print("存在未上电的相机，现给相机上电")
                        power_num += 1
                        print("==============%s" % power_num)
                        if "mkz" in str(vehicle_type):
                            cmd_str = 'mem-test w 0x80000000 0x0020 0xfffff7f0'
                        else:
                            cmd_str = 'mem-test w 0x80000000 0x0020 0xfffffff0'
                        cmd = get_cmd_str(password, cmd_str)
                        info_list = os.popen(cmd).readlines()
            if isp_power_flag:
                break
            else:
                continue
    except Exception as e:
        sensorhub_camera_dick["0检查ISP上电状态"] = e

    # 检查相机lock状态
    try:
        print("检查相机lock状态")
        cmd_str = 'mem-test r 0x80000000 100 4'
        cmd = get_cmd_str(password, cmd_str)
        info_list = os.popen(cmd).readlines()
        lock_flag = True
        for info in info_list:
            if "0x00000100" in info:
                result_list = []
                result_list.append(info.strip().replace("\r", "").replace("\n", ""))
                lock_str = str(info.strip().split(" ")[-3].strip()[:-4])
                lock_int = int(lock_str, 16)
                lock_b = '{:016b}'.format(lock_int)
                lock_b_result = lock_b[:-4][::-1]
                for idx, vsync in enumerate(lock_b_result):
                    if str(idx + 4) in vsync_dict.keys():
                        if "1" in vsync:
                            sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["01相机lock状态"] = "104寄存器lock状态正常, True"
                        else:
                            sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["01相机lock状态"] = "104寄存器lock状态异常, False"
    except Exception as e:
        sensorhub_camera_dick["01相机lock状态"] = e

    #
    # 检查isp错误状态
    if vehicle_type == "mkz":
        cam_isp_list = {'U2': ['10', 'U60'], 'U4': ['12', 'F197'], 'U5': ['13', 'R197'],
                    'U6': ['14', 'Rear197'], 'U7': ['15', 'L197'],
                    'U10': ['4', 'F30'], 'U11': ['5', 'F120'], 'U12': ['6', 'LF100'], 'U13': ['7', 'RF100'],
                    'U14': ['8', 'LR60'], 'U15': ['9', 'RR60']}
    else:
        cam_isp_list = {'U2': ['10', 'U60'], 'U3': ['11', 'D60'], 'U4': ['12', 'F197'], 'U5': ['13', 'R197'],
                    'U6': ['14', 'Rear197'], 'U7': ['15', 'L197'],
                    'U10': ['4', 'F30'], 'U11': ['5', 'F120'], 'U12': ['6', 'LF100'], 'U13': ['7', 'RF100'],
                    'U14': ['8', 'LR60'], 'U15': ['9', 'RR60']}
    isp_list = {}
    if len(cam_list) == 0:
        isp_list = cam_isp_list
    else:
        for key in cam_isp_list.keys():
            if (cam_isp_list[key][0] in vsync_dict.keys()):
                isp_list[key] = cam_isp_list[key]
    try:
        typedef_enum = {
            "0": "system_reset",
            "1": "system_init",
            "2": "system_active",
            "3": "system_lowpower",
            "4": "system_failsafe"
        }

        Gw5FailCodeFatal_e = {
            "0": "gw5_failcode_fatal_cpu_exception",
            "1": "gw5_failcode_fatal_watchdog",
            "2": "gw5_failcode_fatal_oskernel",
            "3": "gw5_failcode_fatal_fw_corrupted",
            "4": "gw5_failcode_fatal_failsafe_forced",
            "255": "gw5_failcode_fatal_none",
        }

        Gw5FailCode_e = {
            "0": "gw5_failcode_init",
            "1": "gw5_failcode_configuration",
            "2": "gw5_failcode_fw",
            "3": "gw5_failcode_voltage",
            "4": "gw5_failcode_high_temperature",
            "5": "gw5_failcode_imgsensor_access",
            "6": "gw5_failcode_imgsensor_init",
            "7": "gw5_failcode_imgsensor_hw",
            "8": "gw5_failcode_imgsensor_not_found",
            "9": "gw5_failcode_imgsensor_disconnected",
            "10": "gw5_mipi_reciver异常",
            "11": "gw5_failcode_input_video_frozen",
            "12": "gw5_failcode_no_output_video",
            "13": "gw5_failcode_output_video_frozen",
            "14": "gw5_failcode_video_pipeline_stalled",
            "15": "gw5_failcode_video_pipeline_hw",
            "16": "gw5_failcode_mipi_receiver",
            "17": "gw5_failcode_i2c0_ctrl_hw",
            "18": "gw5_failcode_i2c1_ctrl_hw",
            "19": "gw5_failcode_can_ctrl_hw",
            "20": "gw5_failcode_spi0_ctrl_hw",
            "21": "gw5_failcode_spi1_ctrl_hw",
            "22": "gw5_failcode_spi_slave_ctrl_hw",
            "23": "gw5_failcode_peripheral_device_hw",
            "24": "gw5_failcode_iqs_overexposure_detected",
            "25": "gw5_failcode_iqs_underexposure_detected",
            "26": "gw5_failcode_serializer_access",
            "27": "gw5_failcode_deserializer_access",
            "28": "gw5_failcode_iqs_low_contrast_detected",
            "29": "gw5_failcode_iqs_color_tint_detected",
            "255": "gw5_failcode_none",
        }
        print("检查0x10错误状态检查")
        for isp_idx in isp_list:
            cmd_str = 'api_cmd -%s 0x10 max' % isp_idx
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            isp_status_info_list = []
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split(" ....")[0].strip())
                    isp_status_info_list.append("第1个字节代表ISP工作状态：0x%s代表ISP当前为%s模式" % (
                        isp_status_list[0], typedef_enum[str(int(isp_status_list[0], 16))]))
                    isp_status_info_list.append("第2个字节代表Gw5FailCodeFatal状态：0x%s代表ISP当前为%s状态" % (
                        isp_status_list[1], Gw5FailCodeFatal_e[str(int(isp_status_list[1], 16))]))
                    isp_status_info_list.append("第3个字节代表导致ISP异常的fail code：0x%s代表ISP当前为%s" % (
                        isp_status_list[2], Gw5FailCode_e[str(int(isp_status_list[2], 16))]))
                    if "02 ff ff 00" in info:
                        isp_status_info_list.append(True)
                    else:
                        isp_status_info_list.append(False)
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict[i])]["--sensorhub_status"] = False
                        sensorhub_status_flag = False
                    sensorhub_camera_dick["相机%s，%s" % (isp_list[isp_idx][0], isp_list[isp_idx][1])]["02isp-0x10错误状态检查"] = isp_status_info_list
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (isp_list[isp_idx][0], isp_list[isp_idx][1])]["02isp-0x10错误状态检查"] = info
    except Exception as e:
        sensorhub_camera_dick["02isp-0x10错误状态检查"] = e

    # 判断FPGA有没有收到ISP的vsync信号
    try:
        cmd_str = 'mem-test r 0x80010000 0 1'
        cmd = get_cmd_str(password, cmd_str)
        info_list = os.popen(cmd).readlines()
        for info in info_list:
            if "0x00000000" in info:
                result_list = []
                result_list.append(info.strip().replace("\r", "").replace("\n", ""))
                isp_flag = "fff" in info.strip().split(" ")[-1][-4:-1]
                isp_str = str(info.strip().split(" ")[-1].strip()[-4:])
                isp_int = int(isp_str, 16)
                isp_b = '{:016b}'.format(isp_int)
                isp_b_result = isp_b[:-4][::-1]
                for idx, vsync in enumerate(isp_b_result):
                    if str(idx + 4) in vsync_dict.keys():
                        if "1" in vsync:
                            sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["03相机vsync信号状态"] = "104寄存器vsync信号状态正常, True"
                        else:
                            sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["03相机vsync信号状态"] = "104寄存器vsync信号状态异常, False"
                            sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["--sensorhub_status"] = False
                            sensorhub_status_flag = False
    except Exception as e:
        sensorhub_camera_dick["03相机vsync信号状态"] = e

    # 检查相机丢失与丢帧计数
    try:
        print("检查相机丢失与丢帧计数")
        cmd_str = 'mem-test r 0x80000000 0 100'
        cmd = get_cmd_str(password, cmd_str)
        info_list = os.popen(cmd).readlines()
        register_info_list = get_camera_register_info(info_list, "0x00000140")
        for idx, register_info in enumerate(register_info_list):
            if str(idx + 4) in vsync_dict.keys():
                register_info_lock_int = int(register_info[:-4], 16)
                register_info_time_int = int(register_info[-4:], 16)
                sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["04丢失与丢帧计数"] = "丢失次数lock_err_cnt lock:%s，丢帧计数 f_lost_cnt:%s" % (register_info_lock_int, register_info_time_int)
    except Exception as e:
        sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["04丢失与丢帧计数"] = e

    # 检测相机的帧间延时
    try:
        print("检测相机的帧间延时")
        cmd_str = 'mem-test r 0x80010000 0 14'
        cmd = get_cmd_str(password, cmd_str)
        info_list = os.popen(cmd).readlines()
        register_info_list = get_camera_register_image_info(info_list, "0x00000010")[1:-3]
        for idx, register_info in enumerate(register_info_list):
            if str(idx + 4) in vsync_dict.keys():
                register_info_delay_time_int = str(int(register_info, 16))[:-6]
                if int(register_info_delay_time_int) != 50:
                    sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["05帧间延时"] = "帧间延时为：%s， 不等于50，False" % register_info_delay_time_int
                else:
                    sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["05帧间延时"] = "帧间延时为：%s， 等于50，True" % register_info_delay_time_int
    except Exception as e:
        sensorhub_camera_dick["相机%s，%s" % (str(idx + 4), vsync_dict[str(idx + 4)])]["05帧间延时"] = e
    
    if vehicle_type == "mkz":
        cam_vsync_dict_new = {'10': ['U2', 'U60'], '12': ['U4', 'F197'], '13': ['U5', 'R197'], '14': ['U6', 'Rear197'], '15': ['U7', 'L197'], '4': ['U10', 'F30'],
                    '5': ['U11', 'F120'], '6': ['U12', 'LF100'], '7': ['U13', 'RF100'], '8': ['U14', 'LR60'], '9': ['U15', 'RR60']}
    else:
        cam_vsync_dict_new = {'10': ['U2', 'U60'], '11': ['U3', 'D60'], '12': ['U4', 'F197'], '13': ['U5', 'R197'], '14': ['U6', 'Rear197'], '15': ['U7', 'L197'], '4': ['U10', 'F30'],
                    '5': ['U11', 'F120'], '6': ['U12', 'LF100'], '7': ['U13', 'RF100'], '8': ['U14', 'LR60'], '9': ['U15', 'RR60']}

    vsync_dict_new = {}
    if len(cam_list) == 0:
        vsync_dict_new = cam_vsync_dict_new
    else:
        for i in cam_list:
            i = str(i)
            vsync_dict_new[i] = cam_vsync_dict_new[i]

    for i in vsync_dict_new:
        # print(sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])])
        # print(sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["isp错误状态检查"][-1])
        #logger.info(sensorhub_camera_dick)
        if sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["02isp-0x10错误状态检查"][-1] is True and ("正常" in sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["01相机lock状态"]) and ("异常" in sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["03相机vsync信号状态"]):
            one_info_1 = ""
            one_info_2 = ""
            one_info_3 = ""
            one_info_4 = ""
            one_info_5 = ""
            one_info_6 = ""
            one_info_7 = ""
            one_info_8 = ""

            two_info_1 = ""
            two_info_2 = ""
            two_info_3 = ""
            two_info_4 = ""
            two_info_5 = ""
            two_info_6 = ""
            two_info_7 = ""
            two_info_8 = ""

            zero_flag_one = False
            zero_flag_two = False

            cmd_str = 'api_cmd -%s 0x18 max' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info = os.popen(cmd).read()
            info_list_one = os.popen(cmd).readlines()
            time.sleep(1)
            info_list_two = os.popen(cmd).readlines()
            payload_list = []
            if "fail" in info.lower():
                sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["06isp-0x18状态"] = "isp状态有误"
                sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict[i])]["--sensorhub_status"] = False
                sensorhub_status_flag = False
            else:
                for owninfo in info_list_one:
                    if "payload" in owninfo.lower():
                        payload_list.append(owninfo.split("       ")[0])
                        info_one = owninfo.split("       ")[0].split(":")[-1].strip()
                        info_one_list = info_one.split(" ")
                        one_info_1 = info_one_list[0]
                        one_info_2 = info_one_list[1]
                        one_info_3 = info_one_list[2]
                        one_info_4 = info_one_list[3]
                        one_info_5 = info_one_list[4]
                        one_info_6 = info_one_list[5]
                        one_info_7 = info_one_list[6]
                        one_info_8 = info_one_list[7]
                        one_info_9 = info_one_list[8]
                        one_info_10 = info_one_list[9]
                        one_info_11 = info_one_list[10]
                        one_info_12 = info_one_list[11]
                        if "00" in info_one_list[-1] and "00" in info_one_list[-2] and "00" in info_one_list[
                            -3] and "00" in info_one_list[-4]:
                            zero_flag_one = True
                for twoinfo in info_list_two:
                    if "payload" in twoinfo.lower():
                        payload_list.append(twoinfo.split("       ")[0])
                        info_two = twoinfo.split("       ")[0].split(":")[-1].strip()
                        info_two_list = info_two.split(" ")
                        two_info_1 = info_two_list[0]
                        two_info_2 = info_two_list[1]
                        two_info_3 = info_two_list[2]
                        two_info_4 = info_two_list[3]
                        two_info_5 = info_two_list[4]
                        two_info_6 = info_two_list[5]
                        two_info_7 = info_two_list[6]
                        two_info_8 = info_two_list[7]
                        two_info_9 = info_two_list[8]
                        two_info_10 = info_two_list[9]
                        two_info_11 = info_two_list[10]
                        two_info_12 = info_two_list[11]
                        if "00" in info_two_list[-1] and "00" in info_two_list[-2] and "00" in info_two_list[
                            -3] and "00" in info_two_list[-4]:
                            zero_flag_two = True

                one_two_flag = True

                check_abs_flag = False
                if one_info_1 == two_info_1 and one_info_2 == two_info_2 and one_info_3 == two_info_3 and one_info_4 == two_info_4 and one_info_5 == two_info_5 and one_info_6 == two_info_6 and one_info_7 == two_info_7 and one_info_8 == two_info_8:
                    one_two_flag = False
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict[i])]["--sensorhub_status"] = False
                    sensorhub_status_flag = False

                if one_two_flag and abs(int(one_info_1.strip().replace("\r", "").replace("\n", ""), 16) - int(
                        one_info_5.strip().replace("\r", "").replace("\n", ""), 16)) < 2 and abs(
                        int(one_info_2.strip().replace("\r", "").replace("\n", ""), 16) - int(
                                one_info_6.strip().replace("\r", "").replace("\n", ""), 16)) < 2 and abs(
                        int(one_info_3.strip().replace("\r", "").replace("\n", ""), 16) - int(
                                one_info_7.strip().replace("\r", "").replace("\n", ""), 16)) < 2 and abs(
                        int(one_info_4.strip().replace("\r", "").replace("\n", ""), 16) - int(
                                one_info_8.strip().replace("\r", "").replace("\n", ""), 16)) < 2 and abs(
                        int(two_info_1.strip().replace("\r", "").replace("\n", ""), 16) - int(
                                two_info_5.strip().replace("\r", "").replace("\n", ""), 16)) < 2 and abs(
                        int(two_info_2.strip().replace("\r", "").replace("\n", ""), 16) - int(
                                two_info_6.strip().replace("\r", "").replace("\n", ""), 16)) < 2 and abs(
                        int(two_info_3.strip().replace("\r", "").replace("\n", ""), 16) - int(
                                two_info_7.strip().replace("\r", "").replace("\n", ""), 16)) < 2 and abs(
                        int(two_info_4.strip().replace("\r", "").replace("\n", ""), 16) - int(
                                two_info_8.strip().replace("\r", "").replace("\n", ""), 16)) < 2:
                    check_abs_flag = True

                payload_list.append("最后四个字节应当全为0：%s" % str(zero_flag_one and zero_flag_two))
                payload_list.append("输入输出帧数应一致或相差1：%s" % str(check_abs_flag))
                payload_list.append("两次数据应当变化：%s" % str(one_two_flag))
                sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["06isp-0x18状态"] = payload_list

            # # Isp SOT Error 计数
            # cmd_str = 'api_cmd -%s 0x2 max 0140005e51' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp SOT Error 计数"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp SOT Error 计数"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp SOT Error 计数"] = info

            # # Isp ECC single ERROR
            # cmd_str = 'api_cmd -%s 0x2 max 0148005e51' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp ECC single ERROR"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp ECC single ERROR"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp ECC single ERROR"] = info

            # # Isp ECC double ERROR
            # cmd_str = 'api_cmd -%s 0x2 max 014c005e51' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp ECC double ERROR"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp ECC double ERROR"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp ECC double ERROR"] = info

            # Isp Crc error 计数
            cmd_str = 'api_cmd -%s 0x2 max 0154005e51' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            isp_status_info_list = []
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                        isp_status_info_list.append("True")
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["07Isp Crc error 计数"] = isp_status_info_list
                    else:
                        isp_status_info_list.append("False")
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["07Isp Crc error 计数"] = isp_status_info_list
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["07Isp Crc error 计数"] = info

            # # Isp电压
            # cmd_str = 'api_cmd -%s 0xd0 max' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # isp_dianya_str = ''
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         isp_dianya_str = str(isp_status_list[-5]) + str(isp_status_list[-6]) + str(isp_status_list[-7]) + str(isp_status_list[-8])
            #         isp_dianya_float = get_float_num(isp_dianya_str)
            #         isp_status_info_list.append(isp_dianya_float)
            #         if float("0.88") >= float(str(isp_dianya_float)[:4]):
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp电压"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp Crc error 计数"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["Isp Crc error 计数"] = info

            # 解串9296 5D寄存器
            cmd_str = 'api_cmd -%s 0xC0 4 900000005D0500000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            isp_status_info_list = []
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                        isp_status_info_list.append("True")
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["08解串9296 5D寄存器"] = isp_status_info_list
                    else:
                        isp_status_info_list.append("False")
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["08解串9296 5D寄存器"] = isp_status_info_list
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["08解串9296 5D寄存器"] = info

            # 解串9296 22寄存器
            cmd_str = 'api_cmd -%s 0xC0 4 90000000220000000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            isp_status_info_list = []
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                        isp_status_info_list.append("True")
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["09解串9296 22寄存器"] = isp_status_info_list
                    else:
                        isp_status_info_list.append("False")
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["09解串9296 22寄存器"] = isp_status_info_list
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["09解串9296 22寄存器"] = info

            # # ISP与解串芯片通信状态
            # cmd_str = 'api_cmd -%s 0xc0 04 900000002f0000000201' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         if "07" in isp_status_list[-4] or "06" in isp_status_list[-4]:
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["ISP与解串芯片通信状态"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["ISP与解串芯片通信状态"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["ISP与解串芯片通信状态"] = info

            # 解串9296通道crc Error状态
            crc_error_9296_flag = True
            cmd_str = 'api_cmd -%s 0xc0 04 90000000000100000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            isp_status_info_list = []
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "23" in isp_status_list[-4]:
                        pass
                    else:
                        crc_error_9296_flag = False
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["10解串9296通道crc Error状态"] = info

            cmd_str = 'api_cmd -%s 0xc0 04 90000000120100000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(
                        info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[
                        -3] and "23" in isp_status_list[-4]:
                        pass
                    else:
                        crc_error_9296_flag = False
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["10解串9296通道crc Error状态"] = info

            cmd_str = 'api_cmd -%s 0xc0 04 90000000240100000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(
                        info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[
                        -3] and "23" in isp_status_list[-4]:
                        pass
                    else:
                        crc_error_9296_flag = False
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["10解串9296通道crc Error状态"] = info

            cmd_str = 'api_cmd -%s 0xc0 04 90000000360100000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(
                        info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[
                        -3] and "23" in isp_status_list[-4]:
                        pass
                    else:
                        crc_error_9296_flag = False
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["10解串9296通道crc Error状态"] = info

            if crc_error_9296_flag:
                isp_status_info_list.append("True")
                sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["10解串9296通道crc Error状态"] = isp_status_info_list
            else:
                isp_status_info_list.append("False")
                sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["10解串9296通道crc Error状态"] = isp_status_info_list

            # 解串9296通道crc异常计数
            crc_9296_flag = True
            cmd_str = 'api_cmd -%s 0xc0 04 900000005c0500000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            isp_status_info_list = []
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                        pass
                    else:
                        crc_9296_flag = False
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["11解串9296通道crc异常计数"] = info

            cmd_str = 'api_cmd -%s 0xc0 04 900000005d0500000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(
                        info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                        pass
                    else:
                        crc_9296_flag = False
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["11解串9296通道crc异常计数"] = info

            cmd_str = 'api_cmd -%s 0xc0 04 900000005e0500000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(
                        info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                        pass
                    else:
                        crc_9296_flag = False
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["11解串9296通道crc异常计数"] = info

            cmd_str = 'api_cmd -%s 0xc0 04 900000005f0500000201' % vsync_dict_new[i][0]
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            for info in info_list:
                if "PAYLOAD[" in info:
                    isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                    isp_status_info_list.append(
                        info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                        pass
                    else:
                        crc_9296_flag = False
                elif "failed" in info or "Failed" in info:
                    sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["11解串9296通道crc异常计数"] = info

            if crc_9296_flag:
                isp_status_info_list.append("True")
                sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["11解串9296通道crc异常计数"] = isp_status_info_list
            else:
                isp_status_info_list.append("False")
                sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["11解串9296通道crc异常计数"] = isp_status_info_list

            # # 串化芯片9295通讯 crc 计数
            # cmd_str = 'api_cmd -%s 0xc0 04 900000001d0400000201' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295通讯 crc 计数"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295通讯 crc 计数"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295通讯 crc 计数"] = info

            # # 串化芯片9295输出端lock
            # cmd_str = 'api_cmd -%s 0xc0 04 90000000130000000201' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295输出端lock"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295输出端lock"] = info

            # # 串化芯片9295输入端mipi 1
            # cmd_str = 'api_cmd -%s 0xc0 04 90000000410300000201' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295输入端mipi 1"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295输入端mipi 1"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295输入端mipi 1"] = info

            # # 串化芯片9295输入端mipi 2
            # cmd_str = 'api_cmd -%s 0xc0 04 80000000420300000201' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295输入端mipi 2"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295输入端mipi 2"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295输入端mipi 2"] = info

            # # 串化芯片9295内存crc检测
            # cmd_str = 'api_cmd -%s 0xc0 04 900000001f0000000201' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295内存crc检测"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295内存crc检测"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295内存crc检测"] = info

            # # 串化芯片9295 pclock检测
            # cmd_str = 'api_cmd -%s 0xc0 04 90000000a01000000201' % vsync_dict_new[i][0]
            # cmd = get_cmd_str(password, cmd_str)
            # info_list = os.popen(cmd).readlines()
            # isp_status_info_list = []
            # for info in info_list:
            #     if "PAYLOAD[" in info:
            #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
            #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
            #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
            #             isp_status_info_list.append("True")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295 pclock检测"] = isp_status_info_list
            #         else:
            #             isp_status_info_list.append("False")
            #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295 pclock检测"] = isp_status_info_list
            #     elif "failed" in info or "Failed" in info:
            #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["串化芯片9295 pclock检测"] = info

            if i == '5' or i == '4':
                # # IMX490 sensor状态
                # cmd_str = 'api_cmd -%s 0xc0 04 34000000707600000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "20" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490 sensor状态"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490 sensor状态"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490 sensor状态"] = info

                # IMX490自检 时钟检测
                cmd_str = 'api_cmd -%s 0xc0 04 3400000014c100000201' % vsync_dict_new[i][0]
                cmd = get_cmd_str(password, cmd_str)
                info_list = os.popen(cmd).readlines()
                isp_status_info_list = []
                for info in info_list:
                    if "PAYLOAD[" in info:
                        isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                        isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                        if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                            isp_status_info_list.append("True")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["12IMX490自检 时钟检测"] = isp_status_info_list
                        else:
                            isp_status_info_list.append("False")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["12IMX490自检 时钟检测"] = isp_status_info_list
                    elif "failed" in info or "Failed" in info:
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["12IMX490自检 时钟检测"] = info

                # IMX490自检 序列错误监控检测
                cmd_str = 'api_cmd -%s 0xc0 04 3400000015c100000201' % vsync_dict_new[i][0]
                cmd = get_cmd_str(password, cmd_str)
                info_list = os.popen(cmd).readlines()
                isp_status_info_list = []
                for info in info_list:
                    if "PAYLOAD[" in info:
                        isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                        isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                        if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                            isp_status_info_list.append("True")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["13IMX490自检 序列错误监控检测"] = isp_status_info_list
                        else:
                            isp_status_info_list.append("False")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["13IMX490自检 序列错误监控检测"] = isp_status_info_list
                    elif "failed" in info or "Failed" in info:
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["13IMX490自检 序列错误监控检测"] = info

                # # IMX490自检 同步信号检测
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000016c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 同步信号检测"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 同步信号检测"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 同步信号检测"] = info

                # # IMX490自检 温度异常检测
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000019c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 温度异常检测"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 温度异常检测"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 温度异常检测"] = info

                # # IMX490自检 RAM ECC检测1
                # cmd_str = 'api_cmd -%s 0xc0 04 340000001ac100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 RAM ECC检测1"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 RAM ECC检测1"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 RAM ECC检测1"] = info

                # # IMX490自检 RAM ECC检测2
                # cmd_str = 'api_cmd -%s 0xc0 04 340000001bc100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 RAM ECC检测2"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 RAM ECC检测2"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 RAM ECC检测2"] = info

                # # IMX490自检 RAM ECC检测3
                # cmd_str = 'api_cmd -%s 0xc0 04 340000001cc100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 RAM ECC检测3"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 RAM ECC检测3"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 RAM ECC检测3"] = info

                # # IMX490自检 OTP CRC检测1
                # cmd_str = 'api_cmd -%s 0xc0 04 340000001dc100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 OTP CRC检测1"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 OTP CRC检测1"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 OTP CRC检测1"] = info

                # # IMX490自检 OTP CRC检测2
                # cmd_str = 'api_cmd -%s 0xc0 04 340000002bc100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 OTP CRC检测2"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 OTP CRC检测2"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 OTP CRC检测2"] = info

                # # IMX490自检 ROM CRC错误检测
                # cmd_str = 'api_cmd -%s 0xc0 04 340000001ec100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 ROM CRC错误检测"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 ROM CRC错误检测"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 ROM CRC错误检测"] = info

                # # IMX490自检 模拟电路检测
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000021c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 模拟电路检测"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 模拟电路检测"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 模拟电路检测"] = info

                # # IMX490自检 信号处理电路检测
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000022c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 信号处理电路检测"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 信号处理电路检测"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 信号处理电路检测"] = info

                # # IMX490自检 寄存器监控检测
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000023c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 寄存器监控检测"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 寄存器监控检测"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 寄存器监控检测"] = info

                # # IMX490自检 内部总线监控检测
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000024c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 内部总线监控检测"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 内部总线监控检测"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 内部总线监控检测"] = info

                # # IMX490自检 电源监控检测1
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000029c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测1"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测1"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测1"] = info

                # # IMX490自检 电源监控检测2
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000026c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测2"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测2"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测2"] = info

                # # IMX490自检 电源监控检测3
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000027c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测3"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测3"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测3"] = info

                # # IMX490自检 电源监控检测4
                # cmd_str = 'api_cmd -%s 0xc0 04 3400000028c100000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测4"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测4"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["IMX490自检 电源监控检测4"] = info

                # IMX490自检 通信CRC检测
                cmd_str = 'api_cmd -%s 0xc0 04 340000002ac100000201' % vsync_dict_new[i][0]
                cmd = get_cmd_str(password, cmd_str)
                info_list = os.popen(cmd).readlines()
                isp_status_info_list = []
                for info in info_list:
                    if "PAYLOAD[" in info:
                        isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                        isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                        if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                            isp_status_info_list.append("True")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["14IMX490自检 通信CRC检测"] = isp_status_info_list
                        else:
                            isp_status_info_list.append("False")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["14IMX490自检 通信CRC检测"] = isp_status_info_list
                    elif "failed" in info or "Failed" in info:
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["14IMX490自检 通信CRC检测"] = info

            else:
                # imx390 sensor状态
                cmd_str = 'api_cmd -%s 0xc0 04 42000000015000000201' % vsync_dict_new[i][0]
                cmd = get_cmd_str(password, cmd_str)
                info_list = os.popen(cmd).readlines()
                isp_status_info_list = []
                for info in info_list:
                    if "PAYLOAD[" in info:
                        isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                        isp_status_info_list.append(
                            info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                        if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "03" in isp_status_list[-4]:
                            isp_status_info_list.append("True")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["15imx390 sensor状态"] = isp_status_info_list
                        else:
                            isp_status_info_list.append("False")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["15imx390 sensor状态"] = isp_status_info_list
                    elif "failed" in info or "Failed" in info:
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["15imx390 sensor状态"] = info

                # Imx390 Sensor 帧计数
                cmd_str = 'api_cmd -%s 0xc0 04 42000000085400000201' % vsync_dict_new[i][0]
                cmd = get_cmd_str(password, cmd_str)
                info_list = os.popen(cmd).readlines()
                isp_status_info_list = []
                for info in info_list:
                    if "PAYLOAD[" in info:
                        isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                        isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    elif "failed" in info or "Failed" in info:
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["16Imx390 Sensor 帧计数"] = info

                info_list = os.popen(cmd).readlines()
                for info in info_list:
                    if "PAYLOAD[" in info:
                        isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                        isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                    elif "failed" in info or "Failed" in info:
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["16Imx390 Sensor 帧计数"] = info
                if len(isp_status_info_list) == 2:
                    if isp_status_info_list[0] not in isp_status_info_list[-1]:
                        isp_status_info_list.append("True")
                    else:
                        isp_status_info_list.append("False")
                else:
                    isp_status_info_list.append("False")
                sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["16Imx390 Sensor 帧计数"] = isp_status_info_list

                # # imx390 自检报错1
                # cmd_str = 'api_cmd -%s 0xc0 04 42000000205400000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(
                #             info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["imx390 自检报错1"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["imx390 自检报错1"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["imx390 自检报错1"] = info

                # # imx390 自检报错2
                # cmd_str = 'api_cmd -%s 0xc0 04 42000000215400000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(
                #             info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                #             isp_status_info_list.append("True")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["imx390 自检报错2"] = isp_status_info_list
                #         else:
                #             isp_status_info_list.append("False")
                #             sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["imx390 自检报错2"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["imx390 自检报错2"] = info

                # imx390 自检报错3
                cmd_str = 'api_cmd -%s 0xc0 04 42000000225400000201' % vsync_dict_new[i][0]
                cmd = get_cmd_str(password, cmd_str)
                info_list = os.popen(cmd).readlines()
                isp_status_info_list = []
                for info in info_list:
                    if "PAYLOAD[" in info:
                        isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                        isp_status_info_list.append(
                            info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                        if "00" in isp_status_list[-1] and "00" in isp_status_list[-2] and "00" in isp_status_list[-3] and "00" in isp_status_list[-4]:
                            isp_status_info_list.append("True")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["17imx390 自检报错3"] = isp_status_info_list
                        else:
                            isp_status_info_list.append("False")
                            sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["17imx390 自检报错3"] = isp_status_info_list
                    elif "failed" in info or "Failed" in info:
                        sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["17imx390 自检报错3"] = info

                # # imx390 自检报错4
                # cmd_str = 'api_cmd -%s 0xc0 04 42000000545400000201' % vsync_dict_new[i][0]
                # cmd = get_cmd_str(password, cmd_str)
                # info_list = os.popen(cmd).readlines()
                # isp_status_info_list = []
                # for info in info_list:
                #     if "PAYLOAD[" in info:
                #         isp_status_list = info.split("             ")[0].split(":")[-1].strip().split(" ")
                #         isp_status_info_list.append(info.strip().replace("\r", "").replace("\n", "").split("             ")[0])
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["imx390 自检报错4"] = isp_status_info_list
                #     elif "failed" in info or "Failed" in info:
                #         sensorhub_camera_dick["相机%s，%s" % (i, vsync_dict_new[i][-1])]["imx390 自检报错4"] = info

    # print("打开isp_monitor")
    # cmd_str = 'isp_monitor &'
    # cmd = get_cmd_str(password, cmd_str)
    # info_list = os.popen(cmd).readlines()
    #print(json.dumps(sensorhub_camera_dick, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))
    # shub_dick = json.dumps(sensorhub_camera_dick, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False)
    sh_dict[loop_time] = sensorhub_camera_dick
    # with open('emc_check.json' , 'a', encoding="utf-8") as f:
    #     # if os.stat('emc_check.json').st_size > 0:
    #     #     f.update(f,shub_dick)
    #     json.dump(sensorhub_camera_dick, f, indent=4, ensure_ascii=False, sort_keys=True, separators=(', ', ': '))
        
    return sensorhub_status_flag, sh_dict

def signal_handler(signal,frame):
    print('You pressed Ctrl + C!')
    print("打开isp_monitor")
    cmd_str = 'isp_monitor &'
    password = "root"
    cmd = get_cmd_str(password, cmd_str)
    info_list = os.popen(cmd).readlines()
    sys.exit(0)
 


def main(config_file, log_file_name, vehicle_type, cam_list):
    print("当前为循环检测")
    print("无需输入密码，等待即可，时间较长，请耐心等待")
    loop_time = 0
    dt = datetime.now()
    dt_str = dt.strftime('%Y_%m_%d_%H_%M_%S')
    restart_isp_monitor = 0
    sh_dict = {}
    while loop_time <  10:
        signal.signal(signal.SIGINT,signal_handler)
        print('输入 Ctrl + C 可退出循环，若退出，则该次检测log无法记录，之前的log存储在时间+车牌+循环次数的文件中')
        loop_time += 1
        print("正在进行第%s次检查" % loop_time)
        sensorhub_status_flag, sh_dict = sh2_check(config_file, log_file_name, vehicle_type, cam_list, loop_time, dt_str, sh_dict)
        if sensorhub_status_flag:
            continue
        else:
            restart_isp_monitor += 1
            if restart_isp_monitor > 1:
                print("在一次异常后已自动打开isp_monitor进行复位，但仍然有异常，退出当前循环检测")
                cmd_str = 'isp_monitor &'
                password = "root"
                cmd = get_cmd_str(password, cmd_str)
                info_list = os.popen(cmd).readlines()
                break
            print("当前存在相机0x10或者0x18或者vsync异常，打开isp_monitor")
            cmd_str = 'isp_monitor &'
            password = "root"
            cmd = get_cmd_str(password, cmd_str)
            info_list = os.popen(cmd).readlines()
            time.sleep(60)
    
    with open('/sensorhub_web_toker/web_toker/templates/result/emc_check_%s.json' % dt_str , 'a', encoding="utf-8") as f:
        # if os.stat('emc_check.json').st_size > 0:
        #     f.update(f,shub_dick)
        json.dump(sh_dict, f, indent=4, ensure_ascii=False, sort_keys=True, separators=(', ', ': '))
        
        
        
        
    


#if __name__ == '__main__':
def start():
    print("首次运行，安装必要库")
    if_install_cmd = "dpkg -l |awk '{print $1,$2}'|grep sshpass"
    if_info = os.popen(if_install_cmd).readline()
    if "sshpass" in if_info:
        pass
    else:
        cmd = "echo 'mm' | sudo -S apt-get install sshpass"
        os.popen(cmd)

    if_install_cmd = "dpkg -l |awk '{print $1,$2}'|grep can-utils"
    if_info = os.popen(if_install_cmd).readline()
    if "can-utils" in if_info:
        pass
    else:
        cmd = "echo 'mm' | sudo -S apt-get install can-utils"
        os.popen(cmd)

    if_lm_sensors_cmd = "dpkg -l |awk '{print $1,$2}'|grep lm-sensors"
    if_sensors_info = os.popen(if_lm_sensors_cmd).readline()
    if "sensors" in if_sensors_info:
        pass
    else:
        cmd = "echo 'mm' | sudo -S apt-get install lm-sensors"
        os.popen(cmd)
    time.sleep(5)
    config_name = os.popen('hostname').read().replace("-", "").strip()
    log_file_name = "sh_2_info.txt"
    while True:
        vehicle_type = 'rx5'
        if vehicle_type != "mkz" and vehicle_type != "rx5":
            print("请输入正确的车型")
            continue
        else:
            break
    # while True:
    #     cam_info = input("请输入想要检查的相机编号（4-15），中间以空格分割，若不输入，则检查全部相机:")
    #     cam_list = list(filter(None, cam_info.split(" ")))
    #     print(cam_list)
    #     break_flag = True
    #     try:
    #         if vehicle_type == "mkz":
    #             for i in cam_list:
    #                 if int(i) == 11:
    #                     print("mkz车型没有第11路相机，请重新输入")
    #                     break_flag = False
    #                 else:
    #                     if 4 <= int(i) <= 15:
    #                         pass
    #                     else:
    #                         print("输入的相机编号只能为4-15，请重新输入")
    #                         break_flag = False
    #             if break_flag:
    #                 break
    #             else:
    #                 continue
    #         else:
    #             for i in cam_list:
    #                 if 4 <= int(i) <= 15:
    #                     pass
    #                 else:
    #                     print("输入的相机编号只能为4-15，请重新输入")
    #                     break_flag = False
    #             if break_flag:
    #                 break
    #             else:
    #                 continue
    #     except Exception as e:
    #         print("请输入数字")
    cam_list = []
    main(config_name, log_file_name, vehicle_type, cam_list)