from __future__ import print_function
import os
import math
import numpy as np
import pandas as pd
import CC_DataPrep as ccd
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
            self.Val['DDEL_DT'] = (self.Val['PY1']/(1+self.Val['PY2']))*self.Val['DOW']*(self.Val['DC_DT']*self.Val['DT_DR'])* (10*60)*1000
            self.print_this(func)

        elif func=='DELTA':
            # self.Val['DELTA'] = self.Val['DELTA_TMINUS1'] + (self.Val['DDEL_DT'] * (10*60)) # dt = 10 min x 60 = 600 sec
            self.Val['DELTA'] = self.Val['DELTA_TMINUS1'] + (self.Val['DDEL_DT']) # dt = 10 min x 60 = 600 sec
            self.print_this(func)

    def Get(self, var):
        

        if var=='From Input Files':
            self.Table['P_Table_TAB'], self.Table['T_Table_TAB'], self.Table['TAB_Properties'] = ccd.Get_File_Inputs(self.Files['tab'],'tab')
            self.Table['P_Table_WAX'], self.Table['T_Table_WAX'], self.Table['WAX_Properties'] = ccd.Get_File_Inputs(self.Files['wax'],'wax')
            self.dfInputs = ccd.Get_File_Inputs(self.Files['xlsx'],'xlsx')
        
        elif var=='PIO_TABIndex':
            self.Val['PIO_TABIndex'] = ccd.Find_Nearest(self.Table['P_Table_TAB'], self.Val['PIO'])
        
        elif var=='TOI_TABIndex':
            self.Val['TOI_TABIndex'] = ccd.Find_Nearest(self.Table['T_Table_TAB'], self.Val['TOI'])
        
        elif var=='RHOO':
            self.Val['RHOO'] = ccd.Get_Property(
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
            self.Val['TW_TABIndex'] = ccd.Find_Nearest(self.Table['T_Table_TAB'], self.Val['TW'])

        elif var=='PIO_WAXIndex':
            self.Val['PIO_WAXIndex'] = ccd.Find_Nearest(self.Table['P_Table_WAX'], self.Val['PIO'])

        elif var=='TW_WAXIndex':
            self.Val['TW_WAXIndex'] = ccd.Find_Nearest(self.Table['T_Table_WAX'], self.Val['TW'])

        elif var=='RHOOW':
            self.Val['RHOOW'] = ccd.Get_Property(
                self.Val['PIO_TABIndex'], self.Val['TW_TABIndex'], self.Table['TAB_Properties']['RHO LIQ']
            )

        elif var=='UOW':
            self.Val['UOW'] =   ccd.Get_Property(
                self.Val['PIO_TABIndex'], self.Val['TW_TABIndex'], self.Table['TAB_Properties']['U LIQ']
            )

        elif var=='MWWW':
            self.Val['MWWW'] =  ccd.Get_Property(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['WAX_Properties']['MW WAX']
            )

        elif var=='MWOW':
            self.Val['MWOW'] =  ccd.Get_Property(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['WAX_Properties']['MW LIQ']
            )

        elif var=='RHOWW':
            self.Val['RHOWW'] =  ccd.Get_Property(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['WAX_Properties']['RHO WAX']
            )

        elif var=='DC_DT':
            self.Val['DC_DT'] = ccd.Find_DC_DT(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['T_Table_WAX'], 
                self.Table['WAX_Properties']['CONCS WAX'], self.Val['CWAXFEED']
            )
        
    def Save_outputs(self):
        Unit = ccd.Abbreviations('Unit')
        Symbol = ccd.Abbreviations('Symbol')

        for col in Symbol.keys():
            if self.Val['Iteration']==1:
                self.dfOutputs.loc['min', Symbol[col]] = Unit[col]
            self.dfOutputs.loc[self.Val['TIME'], Symbol[col]] = ccd.round_sig(self.Val[col],5)

    def print_this(self,func,Get=False):

        if self.track:
            Desc = ccd.Abbreviations('Description')
            Unit = ccd.Abbreviations('Unit')
            Eqn = ccd.Abbreviations('Equation')

            if not Get:

                printnsave('./', '\nCalculating '+func+' :')
                if self.Val['Iteration']==1:
                    printnsave('./', '{}: {}'.format(func, Desc[func]))
                    printnsave('./', '{}'.format(Eqn[func]))
                printnsave('./', '{} = {} {}'.format(func, self.Val[func], Unit[func]))

            else:
                [] = func
                printnsave('./', '\nGetting '+func+' :')
                printnsave('./', '{} ')
            

if __name__ == '__main__':

    Files = {
        'tab': './temp/Dead Oil - Dulang 44 to 35C - OLGA tab - fixed format.tab',
        'wax': './temp/Dead Oil - DULANG 44 to 35C - OLGA WAX.wax',
        'xlsx': './temp/Dataset Level 1.xlsx'
    } 

    Master(Files=Files)