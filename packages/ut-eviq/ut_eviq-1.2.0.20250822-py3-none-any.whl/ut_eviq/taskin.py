"""
This module provides task input classes for the management of Sustainability Risk Rating (SRR) processing.
"""
from ut_dfr.pddf import PdDf
from ut_path.pathnm import PathNm
from ut_xls.pd.ioipathwb import IoiPathWb

from ut_eviq.utils import Evup
from ut_eviq.utils import Evex
from ut_eviq.cfg import Cfg

import pandas as pd

from typing import Any, TypeAlias
TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnPdDf = None | TyPdDf


class TaskIn:

    kwargs_wb = dict(dtype=str, keep_default_na=False, engine='calamine')

    @classmethod
    def evupadm(cls, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD]:
        """
        Administration processsing for evup
        """
        _cfg = kwargs.get('Cfg', Cfg)

        _in_path_evin = PathNm.sh_path(_cfg.InPath.evin, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _aod_evin: Any = IoiPathWb.read_wb_to_aod_or_doaod(
                _in_path_evin, _sheet_adm, **cls.kwargs_wb)

        _in_path_evex = PathNm.sh_path(_cfg.InPath.evex, kwargs)
        _sheet_exp = kwargs.get('sheet_exp', _cfg.sheet_exp)
        _pddf_evex: Any = IoiPathWb.read_wb_to_df_or_dodf(
                _in_path_evex, _sheet_exp, **cls.kwargs_wb)

        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(
                _aod_evin, _pddf_evex, kwargs)

        return _tup_adm

    @classmethod
    def evupdel(cls, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD]:
        """
        Delete processsing for evup
        """
        _cfg = kwargs.get('Cfg', Cfg)

        _in_path_evin = PathNm.sh_path(_cfg.InPath.evin, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _pddf_evin_adm: TnPdDf = IoiPathWb.read_wb_to_df(
                _in_path_evin, _sheet_adm, **cls.kwargs_wb)
        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _aod_evin_del: TnAoD = IoiPathWb.read_wb_to_aod(
                _in_path_evin, _sheet_del, **cls.kwargs_wb)

        _sw_del_use_evex: TyBool = kwargs.get('sw_del_use_evex', True)
        if _sw_del_use_evex:
            _in_path_evex = PathNm.sh_path(_cfg.InPath.evex, kwargs)
            _sheet_exp = kwargs.get('sheet_exp', _cfg.sheet_exp)
            _pddf_evex: TnPdDf = IoiPathWb.read_wb_to_df(
                    _in_path_evex, _sheet_exp, **cls.kwargs_wb)

            _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)
            _tup_del: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_del_use_evex(
                    _aod_evin_del, _pddf_evin_adm, _aod_evex, _pddf_evex, kwargs)
        else:
            _tup_del = Evup.sh_aod_evup_del(
                    _aod_evin_del, _pddf_evin_adm, kwargs)

        return _tup_del

    @classmethod
    def evupreg(
            cls, kwargs: TyDic
    ) -> tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD]:
        """
        Regular processsing for evup
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evin = PathNm.sh_path(_cfg.InPath.evin, kwargs)
        _in_path_evex = PathNm.sh_path(_cfg.InPath.evex, kwargs)
        _sheet_adm = kwargs.get('sheet_adm', _cfg.sheet_adm)
        _sheet_del = kwargs.get('sheet_del', _cfg.sheet_del)
        _sheet_exp = kwargs.get('sheet_exp', _cfg.sheet_exp)

        _pddf_evin_adm: TnPdDf = IoiPathWb.read_wb_to_df(
                _in_path_evin, _sheet_adm, **cls.kwargs_wb)
        _aod_evin_adm: TnAoD = PdDf.to_aod(_pddf_evin_adm)
        _aod_evin_del: TnAoD = IoiPathWb.read_wb_to_aod(
                _in_path_evin, _sheet_del, **cls.kwargs_wb)

        _pddf_evex: TnPdDf = IoiPathWb.read_wb_to_df(
                _in_path_evex, _sheet_exp, **cls.kwargs_wb)
        _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)

        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(
                _aod_evin_adm, _pddf_evex, kwargs)

        _sw_del_use_evex: TyBool = kwargs.get('sw_del_use_evex', True)
        if _sw_del_use_evex:
            _tup_del: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_del_use_evex(
                _aod_evin_del, _pddf_evin_adm, _aod_evex, _pddf_evex, kwargs)
        else:
            _tup_del = Evup.sh_aod_evup_del(
                _aod_evin_del, _pddf_evin_adm, kwargs)

        return _tup_adm + _tup_del

    @classmethod
    def evdomap(cls, kwargs: TyDic) -> TyAoD:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        _cfg = kwargs.get('Cfg', Cfg)
        _in_path_evex = PathNm.sh_path(_cfg.InPath.evex, kwargs)
        _sheet_exp = kwargs.get('sheet_exp', _cfg.sheet_exp)
        _aod_evex: TnAoD = IoiPathWb.read_wb_to_aod(
            _in_path_evex, _sheet_exp, **cls.kwargs_wb)

        _d_ecv_iq2umh_iq = _cfg.Utils.d_ecv_iq2umh_iq
        _aod_evex_new: TyAoD = Evex.map(_aod_evex, _d_ecv_iq2umh_iq)
        return _aod_evex_new
