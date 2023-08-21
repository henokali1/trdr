# -*- coding: utf-8 -*-

import pandas as pd
from pycaret.classification import load_model, predict_model
from fastapi import FastAPI
import uvicorn
from pydantic import create_model

# Create the app
app = FastAPI()

# Load trained Pipeline
model = load_model("loaded_best_pipeline_api")

# Create input/output pydantic models
input_model = create_model("loaded_best_pipeline_api_input", **{'ABER_ZG_5_15': 216.10800170898438, 'ABER_SG_5_15': 219.62347412109375, 'ABER_XG_5_15': 212.592529296875, 'ABER_ATR_5_15': 3.515470027923584, 'ACCBL_20': 216.3528289794922, 'ACCBM_20': 223.86300659179688, 'ACCBU_20': 232.1478271484375, 'AD': 2755964.25, 'ADOSC_3_10': -53300.19921875, 'ADX_14': 35.08140563964844, 'DMP_14': 0.3039870858192444, 'DMN_14': 1.299378514289856, 'ALMA_10_6.0_0.85': 226.1650848388672, 'AMATe_LR_8_21_2': 0.0, 'AMATe_SR_8_21_2': 1.0, 'AO_5_34': -8.847823143005371, 'OBV': 417238.5, 'OBV_min_2': 355986.875, 'OBV_max_2': 417238.5, 'OBVe_4': 433619.625, 'OBVe_12': 513148.28125, 'AOBV_LR_2': 0.0, 'AOBV_SR_2': 1.0, 'APO_12_26': -3.562051296234131, 'AROOND_14': 92.85713958740234, 'AROONU_14': 50.0, 'AROONOSC_14': -42.85714340209961, 'ATRr_14': 3.5491576194763184, 'BBL_5_2.0': 209.7469482421875, 'BBM_5_2.0': 215.57200622558594, 'BBU_5_2.0': 221.3970489501953, 'BBB_5_2.0': 5.404277801513672, 'BBP_5_2.0': 0.45519354939460754, 'BIAS_SMA_26': -0.044987864792346954, 'BOP': 0.6513888835906982, 'AR_26': 56.03158950805664, 'BR_26': 55.91716003417969, 'CCI_14_0.015': -122.05522918701172, 'CDL_DOJI_10_0.1': 0.0, 'CDL_INSIDE': 0.0, 'open_Z_30_1': -3.179823160171509, 'high_Z_30_1': -2.2863361835479736, 'low_Z_30_1': -2.6544406414031982, 'close_Z_30_1': -2.0190703868865967, 'CFO_9': 1.567077398300171, 'CG_10': -5.569648742675781, 'CHOP_14_1_100': 36.84418487548828, 'CKSPl_10_3_20': 223.51734924316406, 'CKSPs_10_3_20': 220.13368225097656, 'CMF_20': -0.32008522748947144, 'CMO_14': -28.551374435424805, 'COPC_11_14_10': -8.472125053405762, 'CTI_12': -0.9191850423812866, 'LDECAY_5': 215.0500030517578, 'DEC_1': 0.0, 'DEMA_10': 214.6687469482422, 'DCL_20_20': 210.00999450683594, 'DCM_20_20': 220.86500549316406, 'DCU_20_20': 231.72000122070312, 'DPO_20': -3.621000051498413, 'EBSW_40_10': -0.990476667881012, 'EFI_13': -60476.2421875, 'EMA_10': 218.95919799804688, 'ENTP_10': 3.286430597305298, 'EOM_14_100000000': -5587.1708984375, 'ER_10': 0.4109855890274048, 'BULLP_13': -2.9065239429473877, 'BEARP_13': -10.106523513793945, 'FISHERT_9_1': -2.3772225379943848, 'FISHERTs_9_1': -1.9735475778579712, 'FWMA_10': 215.31581115722656, 'HA_open': 215.97132873535156, 'HA_high': 217.3000030517578, 'HA_low': 210.10000610351562, 'HA_close': 213.20249938964844, 'HILO_13_21': 224.16539001464844, 'HILOs_13_21': 224.16539001464844, 'HL2': 213.6999969482422, 'HLC3': 214.14999389648438, 'HMA_10': 212.09877014160156, 'HWM': 218.05133056640625, 'HWU': 223.2996063232422, 'HWL': 212.8030548095703, 'HWMA_0.2_0.1_0.1': 218.05133056640625, 'ISA_9': 226.54750061035156, 'ISB_26': 229.25, 'ITS_9': 219.3249969482422, 'IKS_26': 221.11500549316406, 'ICS_26': 225.52000427246094, 'INC_1': 1.0, 'INERTIA_20_14': 35.80366516113281, 'JMA_7_0': 212.14492797851562, 'KAMA_10_2_30': 219.6112518310547, 'KCLe_20_2': 214.72938537597656, 'KCBe_20_2': 222.1717071533203, 'KCUe_20_2': 229.61402893066406, 'K_9_3': 17.402790069580078, 'D_9_3': 21.77545928955078, 'J_9_3': 8.657449722290039, 'KST_10_15_20_30_10_10_10_15': -2682.972412109375, 'KSTs_9': -1359.4271240234375, 'KURT_30': 1.5752427577972412, 'KVO_34_55_13': -1286.615234375, 'KVOs_34_55_13': -603.803955078125, 'LR_14': 215.76153564453125, 'LOGRET_1': 0.022240377962589264, 'MACD_12_26_9': -3.5189762115478516, 'MACDh_12_26_9': -1.350976586341858, 'MACDs_12_26_9': -2.167999505996704, 'MAD_30': 3.858599901199341, 'MASSI_9_25': 24.11639404296875, 'MCGD_10': 221.1426544189453, 'MEDIAN_30': 227.01499938964844, 'MFI_14': 24.39337158203125, 'MIDPOINT_2': 212.68499755859375, 'MIDPRICE_2': 213.65499877929688, 'MOM_10': -10.550000190734863, 'NATR_14': 1.8695052862167358, 'NVI_1': 1057.165771484375, 'OHLC4': 213.20249938964844, 'PDIST': 9.75, 'PCTRET_1': 0.02248954027891159, 'PGO_14': -2.3348145484924316, 'PPO_12_26_9': -1.581865668296814, 'PPOh_12_26_9': -0.6972943544387817, 'PPOs_12_26_9': -0.8845713138580322, 'PSARs_0.02_0.2': 223.34515380859375, 'PSARaf_0.02_0.2': 0.14000000059604645, 'PSARr_0.02_0.2': 0.0, 'PSL_12': 33.33333206176758, 'PVI_1': 991.1860961914062, 'PVO_12_26_9': 20.450246810913086, 'PVOh_12_26_9': 25.384784698486328, 'PVOs_12_26_9': -4.934537410736084, 'PVOL': 13172156.0, 'PVR': 2.0, 'PVT': -2100876.75, 'PWMA_10': 220.6125030517578, 'QQE_14_5_4.236': 38.3930549621582, 'QQE_14_5_4.236_RSIMA': 33.13190841674805, 'QQEs_14_5_4.236': 38.3930549621582, 'QS_10': -1.0540000200271606, 'QTL_30_0.5': 227.01499938964844, 'RMA_10': 221.94314575195312, 'ROC_10': -4.676418304443359, 'RSI_14': 35.72431182861328, 'RSX_14': 22.557619094848633, 'RVGI_14_4': -0.29659077525138855, 'RVGIs_14_4': -0.2829420864582062, 'RVI_14': 36.99811935424805, 'SINWMA_14': 223.04934692382812, 'SKEW_30': -1.4043824672698975, 'SLOPE_1': 4.730000019073486, 'SMA_10': 220.5919952392578, 'SMI_5_20_5': -0.39424338936805725, 'SMIs_5_20_5': -0.34115010499954224, 'SMIo_5_20_5': -0.053093284368515015, 'SQZ_20_2.0_20_1.5': -10.006667137145996, 'SQZ_ON': 0.0, 'SQZ_OFF': 1.0, 'SQZ_NO': 0.0, 'SQZPRO_20_2.0_20_2_1.5_1': -10.006667137145996, 'SQZPRO_ON_WIDE': 0.0, 'SQZPRO_ON_NORMAL': 0.0, 'SQZPRO_ON_NARROW': 0.0, 'SQZPRO_OFF': 1.0, 'SQZPRO_NO': 0.0, 'SSF_10_2': 214.30776977539062, 'STC_10_12_26_0.5': 0.0, 'STCmacd_10_12_26_0.5': -3.5189762115478516, 'STCstoch_10_12_26_0.5': 0.0, 'STDEV_30': 5.254397869110107, 'STOCHk_14_3_3': 12.905707359313965, 'STOCHd_14_3_3': 9.14327621459961, 'STOCHRSIk_14_14_3_3': 13.987195014953613, 'STOCHRSId_14_14_3_3': 4.662398338317871, 'SUPERT_7_3.0': 224.24571228027344, 'SUPERTd_7_3.0': -1.0, 'SUPERTs_7_3.0': 224.24571228027344, 'SWMA_10': 220.6146697998047, 'T3_10_0.7': 222.1425323486328, 'TEMA_10': 212.8263397216797, 'THERMO_20_2_0.5': 0.30000001192092896, 'THERMOma_20_2_0.5': 1.9809330701828003, 'THERMOl_20_2_0.5': 1.0, 'THERMOs_20_2_0.5': 0.0, 'TOS_STDEVALL_LR': -254.6202392578125, 'TOS_STDEVALL_L_1': -1685.319580078125, 'TOS_STDEVALL_U_1': 1176.0791015625, 'TOS_STDEVALL_L_2': -3116.01904296875, 'TOS_STDEVALL_U_2': 2606.778564453125, 'TOS_STDEVALL_L_3': -4546.71826171875, 'TOS_STDEVALL_U_3': 4037.477783203125, 'TRIMA_10': 221.4472198486328, 'TRIX_30_9': -0.09900528937578201, 'TRIXs_30_9': -0.09504754096269608, 'TRUERANGE_1': 7.199999809265137, 'TSI_13_25_13': -25.93445587158203, 'TSIs_13_25_13': -14.481460571289062, 'TTM_TRND_6': -1.0, 'UI_14': 3.9450087547302246, 'UO_7_14_28': 36.701751708984375, 'VAR_30': 27.608699798583984, 'VHF_28': 0.3782706558704376, 'VIDYA_14': 225.24415588378906})
output_model = create_model("loaded_best_pipeline_api_output", prediction='long')


# Define predict function
@app.post("/predict", response_model=output_model)
def predict(data: input_model):
    data = pd.DataFrame([data.dict()])
    predictions = predict_model(model, data=data)
    return {"prediction": predictions["prediction_label"].iloc[0]}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
