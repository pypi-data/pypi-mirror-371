"""
This module provides task input classes for the management of Sustainability Risk Rating (SRR) processing.
"""
from ut_dfr.pddf import PdDf

from ut_eviq.utils import Evex
from ut_eviq.utils import Evin
from ut_eviq.utils import Evup
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
        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(
                Evin.read_wb_adm_to_aod(kwargs),
                Evex.read_wb_to_df(kwargs),
                kwargs)
        return _tup_adm

    @classmethod
    def evupdel(cls, kwargs: TyDic) -> tuple[TnAoD, TyDoAoD]:
        """
        Delete processsing for evup
        """
        _aod_evin_del: TnPdDf = Evin.read_wb_del_to_aod(kwargs)
        _pddf_evin_adm: TnPdDf = Evin.read_wb_adm_to_df(kwargs)

        _sw_del_use_evex: TyBool = kwargs.get('sw_del_use_evex', True)
        if _sw_del_use_evex:
            _pddf_evex: TnPdDf = Evex.read_wb_exp_to_df(kwargs)
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
        _pddf_evin_adm: TnPdDf = Evin.read_wb_adm_to_df(kwargs)
        _aod_evin_adm: TnAoD = PdDf.to_aod(_pddf_evin_adm)
        _pddf_evex: TnPdDf = Evex.read_wb_to_df(kwargs)
        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(
                _aod_evin_adm, _pddf_evex, kwargs)

        _aod_evin_del: TnPdDf = Evin.read_wb_del_to_aod(kwargs)

        _sw_del_use_evex: TyBool = kwargs.get('sw_del_use_evex', True)
        if _sw_del_use_evex:
            _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)
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
        _aod_evex_new: TyAoD = Evex.map(
                Evex.read_wb_exp_to_aod(kwargs),
                _cfg.Utils.d_ecv_iq2umh_iq)
        return _aod_evex_new
