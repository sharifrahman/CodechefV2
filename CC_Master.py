from __future__ import print_function
import os
import math
import numpy as np
import pandas as pd
import CC_DataPrep as CCD
from printandsave import printnsave

class Master():

    def __init__(
        self, Files, 
        C1=15, C2=0.055, C3=1.4, 
        DI=0.0446, MO=0.50369, 
        PIO= 101325, TOI=46,
        DowMethod = 'Wilke-Chang', track=False
    
    ): 
        if os.path.isfile('./printout.txt'):
            os.remove('./printout.txt')
        self.Val = {'C1':C1, 'C2':C2, 'C3':C3, 'DI':DI, 'MO':MO, 'PIO':PIO, 'TOI':TOI, 'DOWMethod':DowMethod}
        self.Table = {}
        self.Files = Files
        self.track = track
        
        self.Unit = CCD.Abbreviations('Unit')
        self.Desc = CCD.Abbreviations('Description')
        self.dfOutputs = pd.DataFrame()

        self.Get('From Input Files')
        self.Get('PIO_TABIndex')
        self.Get('TOI_TABIndex')
        self.Get('RHOO')
        self.Get('CWAXFEED')
        self.Val['DELTA'] = 0 # For iteration no. 1

        for Iteration, Time in enumerate(self.dfInputs.index.values):
            self.Val['Iteration'] = Iteration+1
            self.Val['TIME'] = Time
            if self.track:
                printnsave('./', '\nIteration no. {} \tTime {} min'.format(Iteration+1, Time))

            # To get input variables from input files. 
            # Some input variables derive from interpolation if exact Pressure and Temperature indices not met.
            self.Get('TW')
            self.Get('DW')
            self.Get('DT_DR')
            self.Get('DELTA_TMINUS1')
            self.Get('TW_TABIndex')            
            self.Get('PIO_WAXIndex') 
            self.Get('TW_WAXIndex') 
            self.Get('RHOOW')
            self.Get('UOW')
            self.Get('MWWW')            
            self.Get('MWOW')            
            self.Get('RHOWW')            
            self.Get('DC_DT')
            self.Calc('VO')
            self.Calc('DELD')
            self.Calc('NSR')
            self.Calc('REOW')
            self.Calc('FO')
            self.Calc('FW')
            self.Calc('PY1')
            self.Calc('PY2')
            self.Calc('MVWW')
            self.Calc('DOW')
            self.Calc('DDEL_DT')
            self.Calc('DELTA')

            self.Save_outputs()
            
        self.dfOutputs.index.name = 'TIME'

    def Calc(self,func):

        if func=='VO':
            self.Val['QO'] = self.Val['MO'] / self.Val['RHOO']
            self.Val['VO'] = self.Val['QO'] / (math.pi*math.pow(self.Val['DW']/2,2))
            self.print_this(func)

        elif func=='DELD':
            self.Val['DELD'] = 0.5*(self.Val['DI'] - self.Val['DW'])
            self.print_this(func)

        elif func=='NSR':
            self.Val['NSR'] = (self.Val['RHOOW'] * self.Val['VO'] * self.Val['DELD']) / self.Val['UOW']
            self.print_this(func)

        elif func=='REOW':
            self.Val['REOW'] = (self.Val['RHOOW'] * self.Val['VO'] * self.Val['DW']) / self.Val['UOW']
            self.print_this(func)

        elif func=='FO':
            self.Val['FO'] = 100*(1-((self.Val['REOW']**0.15)/8))
            self.print_this(func)

        elif func=='FW':
            self.Val['FW'] = 1-(self.Val['FO']/100)
            self.print_this(func)

        elif func=='PY1':
            self.Val['PY1'] = self.Val['C1'] / (1-(self.Val['FO']/100))
            self.print_this(func)

        elif func=='PY2':
            self.Val['PY2'] = self.Val['C2'] * (self.Val['NSR']**self.Val['C3'])
            self.print_this(func)

        elif func=='MVWW':
            self.Val['MVWW'] = self.Val['MWWW'] / (0.001*self.Val['RHOWW']) # RHO kg/m3 to g/cm3
            self.print_this(func)
            
        elif func=='DOW':

            TW = self.Val['TW'] + 273.15 # DEG C TO KELVIN
            UOW = self.Val['UOW'] * 1000 # Pa.s to mPa.s

            if self.Val['DOWMethod']=='Wilke-Chang':
                self.Val['DOW'] = 7.4E-12 * ((TW*math.pow(self.Val['MWOW'],0.5))/(UOW*math.pow(self.Val['MVWW'],0.6)))
            elif self.Val['DOWMethod']=='Hayduk-Minhass':
                self.Val['DOW'] = 13.3E-12 * ((math.pow(TW,1.47)*math.pow(UOW,(10.2/self.Val['MVWW'])-0.791))/math.pow(self.Val['MVWW'],0.71))
            self.print_this(func)

        elif func=='DDEL_DT':
            self.Val['DDEL_DT'] = (self.Val['PY1']/(1+self.Val['PY2']))*self.Val['DOW']*(self.Val['DC_DT']*self.Val['DT_DR'])
            self.print_this(func)

        elif func=='DELTA':
            self.Val['DELTA'] = self.Val['DELTA_TMINUS1'] + (self.Val['DDEL_DT'] * (10*60)) # dt = 10 min x 60 = 600 sec
            # self.Val['DELTA'] = self.Val['DELTA_TMINUS1'] + (self.Val['DDEL_DT']) # dt = 10 min x 60 = 600 sec
            self.print_this(func)

    def Get(self, var):
        

        if var=='From Input Files':
            self.Table['P_Table_TAB'], self.Table['T_Table_TAB'], self.Table['TAB_Properties'] = CCD.Get_File_Inputs(self.Files['tab'],'tab')
            self.Table['P_Table_WAX'], self.Table['T_Table_WAX'], self.Table['WAX_Properties'] = CCD.Get_File_Inputs(self.Files['wax'],'wax')
            self.dfInputs = CCD.Get_File_Inputs(self.Files['xlsx'],'xlsx')
        
        elif var=='PIO_TABIndex':
            self.Val['PIO_TABIndex'] = CCD.Find_Nearest(self.Table['P_Table_TAB'], self.Val['PIO'])
        
        elif var=='TOI_TABIndex':
            self.Val['TOI_TABIndex'] = CCD.Find_Nearest(self.Table['T_Table_TAB'], self.Val['TOI'])
        
        elif var=='RHOO':
            self.Val['RHOO'] = CCD.Get_Property(
                self.Val['PIO_TABIndex'], self.Val['TOI_TABIndex'], self.Table['TAB_Properties']['RHO LIQ']
            )

        elif var=='CWAXFEED':
            self.Val['CWAXFEED'] = sum(self.Table['WAX_Properties']['CWAXFEED'])

        elif var=='TW':
            self.Val['TW'] = self.dfInputs.loc[self.Val['TIME'],'Tw']

        elif var=='DW':
            self.Val['DW'] = self.dfInputs.loc[self.Val['TIME'],'dw'] * 0.001 # mm to m

        elif var=='DT_DR':
            self.Val['DT_DR'] = self.dfInputs.loc[self.Val['TIME'],'dT/dr']

        elif var=='DELTA_TMINUS1':
            self.Val['DELTA_TMINUS1'] = self.Val['DELTA'] # DELTA of previous iteration

        elif var=='TW_TABIndex':
            self.Val['TW_TABIndex'] = CCD.Find_Nearest(self.Table['T_Table_TAB'], self.Val['TW'])

        elif var=='PIO_WAXIndex':
            self.Val['PIO_WAXIndex'] = CCD.Find_Nearest(self.Table['P_Table_WAX'], self.Val['PIO'])

        elif var=='TW_WAXIndex':
            self.Val['TW_WAXIndex'] = CCD.Find_Nearest(self.Table['T_Table_WAX'], self.Val['TW'])

        elif var=='RHOOW':
            self.Val['RHOOW'] = CCD.Get_Property(
                self.Val['PIO_TABIndex'], self.Val['TW_TABIndex'], self.Table['TAB_Properties']['RHO LIQ']
            )

        elif var=='UOW':
            self.Val['UOW'] =   CCD.Get_Property(
                self.Val['PIO_TABIndex'], self.Val['TW_TABIndex'], self.Table['TAB_Properties']['U LIQ']
            )

        elif var=='MWWW':
            self.Val['MWWW'] =  CCD.Get_Property(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['WAX_Properties']['MW WAX']
            )

        elif var=='MWOW':
            self.Val['MWOW'] =  CCD.Get_Property(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['WAX_Properties']['MW LIQ']
            )

        elif var=='RHOWW':
            self.Val['RHOWW'] =  CCD.Get_Property(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['WAX_Properties']['RHO WAX']
            )

        elif var=='DC_DT':
            self.Val['DC_DT'] = CCD.Find_DC_DT(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['T_Table_WAX'], 
                self.Table['WAX_Properties']['CONCS WAX'], self.Val['CWAXFEED']
            )
        
    def Save_outputs(self):
        Unit = CCD.Abbreviations('Unit')
        self.dfOutputs.loc[self.Val['TIME'], 'Time'+' ('+Unit['TIME']+')'] = self.Val['TIME']
        self.dfOutputs.loc[self.Val['TIME'], 'Tw'+' ('+Unit['TW']+')']     = self.Val['TW']
        self.dfOutputs.loc[self.Val['TIME'], 'Vo'+' ('+Unit['VO']+')']     = np.round(self.Val['VO'],5)
        self.dfOutputs.loc[self.Val['TIME'], 'RhoWw'+' ('+Unit['RHOWW']+')'] = np.round(self.Val['RHOWW'],3)
        self.dfOutputs.loc[self.Val['TIME'], 'MVWW'+' ('+Unit['MVWW']+')'] = np.round(self.Val['MVWW'],3)
        self.dfOutputs.loc[self.Val['TIME'], 'MWOW'+' ('+Unit['MWOW']+')']     = CCD.round_sig(self.Val['MWOW'],5)
        self.dfOutputs.loc[self.Val['TIME'], '\u03B4d'+' (mm)']            = np.round(self.Val['DELD']*1000,3)
        self.dfOutputs.loc[self.Val['TIME'], 'Nsr']                        = np.round(self.Val['NSR'],3)
        self.dfOutputs.loc[self.Val['TIME'], 'Reow']                       = np.round(self.Val['REOW'],3)
        self.dfOutputs.loc[self.Val['TIME'], 'Fo'+' ('+Unit['FO']+')']     = np.round(self.Val['FO'],3)
        self.dfOutputs.loc[self.Val['TIME'], 'Fw'+' ('+Unit['FW']+')']     = np.round(self.Val['FW'],6)
        self.dfOutputs.loc[self.Val['TIME'], '\u03C0₁']                    = np.round(self.Val['PY1'],3)
        self.dfOutputs.loc[self.Val['TIME'], '\u03C0₂']                    = np.round(self.Val['PY2'],3)
        self.dfOutputs.loc[self.Val['TIME'], 'Dow'+' (m²/s)']              = CCD.round_sig(self.Val['DOW'],4)
        self.dfOutputs.loc[self.Val['TIME'], 'dC/dT']                      = CCD.round_sig(self.Val['DC_DT'])
        self.dfOutputs.loc[self.Val['TIME'], 'd\u03B4/dt'+' (mm/s)']       = CCD.round_sig(self.Val['DDEL_DT']*1000) # m/s to mm/s
        self.dfOutputs.loc[self.Val['TIME'], '\u03B4'+' (mm)']             = CCD.round_sig(self.Val['DELTA'] *1000) # m to mm

    def print_this(self,func):

        if self.track:
            Desc = CCD.Abbreviations('Description')
            Unit = CCD.Abbreviations('Unit')
            Eqn = CCD.Abbreviations('Equation')

            printnsave('./', '\nCalculating '+func+' :\n')
            if self.Val['Iteration']==1:
                printnsave('./', '\n{}: {}'.format(func, Desc[func]))
                printnsave('./', '\n{}'.format(Eqn[func]))
            printnsave('./', '\n{} = {} {}'.format(func, self.Val[func], Unit[func]))
    
# if __name__ == '__main__':

#     Files = {
#         'tab': './temp/Dead Oil - Dulang 44 to 35C - OLGA tab - fixed format.tab',
#         'wax': './temp/Dead Oil - DULANG 44 to 35C - OLGA WAX.wax',
#         'xlsx': './temp/Dataset Level 1.xlsx'
#     } 

#     Master(Files=Files)