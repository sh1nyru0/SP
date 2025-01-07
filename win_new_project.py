import json
from threading import Thread

import pymysql
from PyQt5.QtWidgets import QFileDialog
from qtpy import uic

from libs.share import MySignals

gms = MySignals()

class New_Project:
    def __init__(self):
        self.ui = uic.loadUi('new_project.ui')
        self.ui.choose_location.clicked.connect(self.chooseLocation)
        self.ui.btn_ok.clicked.connect(self.onOk)
        self.ui.btn_cancel.clicked.connect(self.onCancel)

    def chooseLocation(self):
        filePath = QFileDialog.getExistingDirectory(self.ui, "选择存储路径")
        self.ui.project_location.setText(filePath)

    def onOk(self):
        import os
        def threadFunc():
            name = self.ui.project_name.text()
            location = self.ui.project_location.text()
            project = '{}/{}'.format(location,name)
            connection = pymysql.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                password='123456',
                charset='utf8'
            )
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name}")
            cursor.execute(f"USE {name}")
            cursor.execute("""
                CREATE TABLE gravity_data(
                    id             int auto_increment
                        primary key,
                    Filename       varchar(100) null,
                    Line_no        varchar(100) not null,
                    Flight_ID      varchar(100) not null,
                    Lon            varchar(100) not null,
                    Lat            varchar(100) not null,
                    x              varchar(100) null,
                    y              varchar(100) null,
                    Height_WGS1984 varchar(100) null,
                    Date           varchar(100) null,
                    Time           varchar(100) null,
                    ST             varchar(100) null,
                    CC             varchar(100) null,
                    RB             varchar(100) null,
                    XACC           varchar(100) null,
                    LACC           varchar(100) null,
                    Still          varchar(100) null,
                    Base           varchar(100) null,
                    ST_real        varchar(100) null,
                    Beam_vel       varchar(100) null,
                    rec_grav       varchar(100) null,
                    Abs_grav       varchar(100) null,
                    VaccCor        varchar(100) null,
                    EotvosCor      varchar(100) null,
                    FaCor          varchar(100) null,
                    HaccCor        varchar(100) null,
                    Free_air       varchar(100) null,
                    FAA_filt       varchar(100) null,
                    FAA_clip       varchar(100) null,
                    Level_cor      varchar(100) null,
                    FAA_level      varchar(100) null,
                    Fa_4600m       varchar(100) null
                )
            """)
            cursor.execute("""
                CREATE TABLE electro_data(
                    id          int auto_increment
                        primary key,
                    Filename    varchar(100) null,
                    opnum       varchar(100) null,
                    freq        varchar(100) null,
                    comp        varchar(100) null,
                    ampa        varchar(100) null,
                    emag        varchar(100) null,
                    ephz        varchar(100) null,
                    hmag        varchar(100) null,
                    hphz        varchar(100) null,
                    resistivity varchar(100) null,
                    phase       varchar(100) null,
                    rho         varchar(100) null,
                    phz         varchar(100) null
                )
            """)
            cursor.execute("""
                CREATE TABLE gama_data(
                    id       int auto_increment
                        primary key,
                    Filename varchar(100) null,
                    Lon      varchar(100) null,
                    Lat      varchar(100) null,
                    kc       varchar(100) null,
                    thc      varchar(100) null,
                    uc       varchar(100) null
                )
            """)
            cursor.execute("""
                CREATE TABLE gps_data(
                    id       int auto_increment
                        primary key,
                    Filename varchar(100) null,
                    FH       varchar(100) null,
                    UCTCT    varchar(100) null,
                    Lon      varchar(100) null,
                    Lat      varchar(100) null,
                    Vel      varchar(100) null,
                    UTCD     varchar(100) null
                )
            """)
            cursor.execute("""
                CREATE TABLE hyper_data(
                    id          int auto_increment
                        primary key,
                    Filename    varchar(100) null,
                    content     varchar(200) null,
                    description varchar(100) null,
                    samples     varchar(100) null,
                    `lines`     varchar(100) null,
                    bands       varchar(100) null,
                    type        varchar(100) null,
                    len         varchar(100) null
                )
            """)
            cursor.execute("""
                CREATE TABLE magnetic_data(
                    id             int auto_increment
                        primary key,
                    Filename       varchar(200) null,
                    Line_name      varchar(200) not null,
                    point          varchar(200) not null,
                    lon            varchar(200) not null,
                    lat            varchar(200) not null,
                    x              varchar(200) null,
                    y              varchar(200) null,
                    Height_WGS1984 varchar(200) null,
                    Date           varchar(200) null,
                    MagR           varchar(200) null,
                    Magc           varchar(200) null,
                    RefField       varchar(200) null,
                    MagRTC         varchar(200) null,
                    BCorr          varchar(200) null,
                    MagBRTC        varchar(200) null,
                    ACorr          varchar(200) null,
                    MagF           varchar(200) null,
                    MagL           varchar(200) null,
                    MagML          varchar(200) null,
                    MagML_Drape    varchar(200) null
                )
            """)
            cursor.execute("""
                CREATE TABLE sar_data(
                    id        int auto_increment
                        primary key,
                    Filename  varchar(100) null,
                    content   varchar(100) null,
                    size      varchar(100) null,
                    type      varchar(100) null,
                    direction varchar(100) null,
                    proj      varchar(100) null
                )
            """)
            cursor.execute("""
                CREATE TABLE seg_data(
                    id       int auto_increment
                        primary key,
                    Filename varchar(100) null,
                    opnum    varchar(100) null,
                    olnum    varchar(100) null,
                    ns       varchar(100) null,
                    dt       varchar(100) null,
                    e        varchar(100) null,
                    n        varchar(100) null,
                    ampl     varchar(100) null
                )
            """)
            os.makedirs(project + "/" + "重力数据", exist_ok=True)
            os.makedirs(project + "/" + "磁法数据", exist_ok=True)
            os.makedirs(project + "/" + "放射性数据", exist_ok=True)
            os.makedirs(project + "/" + "电法数据", exist_ok=True)
            os.makedirs(project + "/" + "gps数据", exist_ok=True)
            os.makedirs(project + "/" + "地震数据", exist_ok=True)
            os.makedirs(project + "/" + "地基合成孔径雷达数据", exist_ok=True)
            os.makedirs(project + "/" + "高光谱数据", exist_ok=True)
            os.makedirs(project + "/" + "模型", exist_ok=True)
            jsonItem = {}
            jsonItem["name"] = name
            jsonItem["location"] = location
            jsonItem["project"] = project
            with open('category.json', 'r', encoding='utf8') as f:
                jsonStr = f.read()
            jsonData = json.loads(jsonStr)
            jsonData.append(jsonItem)
            jsonStr = json.dumps(jsonData,ensure_ascii=False,indent=2)
            with open('category.json', 'w', encoding='utf8') as f:
                f.write(jsonStr)
            gms.project.emit()
        Thread(target=threadFunc).start()
        self.ui.close()

    def onCancel(self):
        self.ui.close()