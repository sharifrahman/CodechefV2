import os
import math
import numpy as np
import pandas as pd
import CC_DataPrep as ccd

class Master():

    def __init__(
        self, Files, 
        C1=15, C2=0.055, C3=1.4, 
        DI=0.0446, MO=0.50369, 
        PIO= 101325, TOI=46,
        DowMethod = 'Wilke-Chang'
    ): 
        '''
        Within this Class, we define five (5) Instance Variables:

            [1] Val         Dictionary that maps abbreviations to its corresponding values.

            [2] Table       Dictionary that maps Pressure, Temperature and corresponding Properties from 
                            TAB and WAX files.

            [3] dfInputs    Dataframe of input dataset Tw, dw & dT/dr with simulation time as iteration 
                            index from 0 to 300 min with time step of 10 min.
                            
            [4] dfOutputs   Dataframe of output dataset defined in Symbols attribute.

            [5] Files       List of input files (TAB, WAX & Excel files)

        For code efficiency, we use only two (2) main Class Methods:

            [1] Get         Acquiring parameter values either from :
                            [1] Directly from input dataset table (excel), at given simulation time index.
                            [2] Directly from WAX or TAB file.
                            [3] Interpolate using acquired Parameter tables.
                            All values will be saved under Val and Table dictionaries.

            [2] Calc        Step by step calculation (12 steps) of Wax Loop algorithm
            
        '''
        if os.path.isfile('./printout.txt'):
            os.remove('./printout.txt')

        ## Assigning all user defined parameters as Val dictionary keys and values :
        self.Val = {
            'C1':C1, 'C2':C2, 'C3':C3,
            'DI':DI, 'MO':MO, 
            'PIO':PIO, 'TOI':TOI, 
            'DOWMethod':DowMethod
        }

        ## Creating Table empty dictionary :
        self.Table = {}

        ## Converting the user defined input file names as instance variable list :
        self.Files = Files

        ## Creating dfOutput empty dataframe :
        self.dfOutputs = pd.DataFrame()

        ## Reading from the TAB and WAX files :
        self.Get('From Input Files')

        ## Transform Pio and Toi into index numbers according on TAB and WAX Pressure and Temperature tables :
        self.Get('PIO_TABIndex')
        self.Get('PIO_WAXIndex') 
        self.Get('TOI_TABIndex')

        ## Acquiring ρo from TAB properties using Pio and Toi as index pointer :
        self.Get('RHOO')

        ## Acquiring Total Wax Conc in Feed from TAB properties table :
        self.Get('CWAXFEED')

        ## For iteration #1 we assume δt-1 is zero :
        self.Val['DELTA'] = 0

        for Iteration, Time in enumerate(self.dfInputs.index.values):
            self.Val['Iteration'] = Iteration + 1
            self.Val['TIME'] = Time

            ## Acquiring Tw, dw and dT/dr from dfInputs dataframe :
            self.Get('TW')
            self.Get('DW')
            self.Get('DT_DR')

            ## δt-1 is equal to δ of previous iteration :
            self.Get('DELTA_TMINUS1')

            ## Transform Tw into index numbers according on TAB and WAX Pressure and Temperature tables :
            self.Get('TW_TABIndex')            
            self.Get('TW_WAXIndex') 

            ## Acquiring ρow and μow from TAB properties using Pio and Tw as index pointer :
            self.Get('RHOOW')
            self.Get('UOW')

            ## Acquiring MWww, MWow, ρww and dC/dT from WAX properties using Pio and Tw as index pointer :
            self.Get('MWWW')            
            self.Get('MWOW')            
            self.Get('RHOWW')            
            self.Get('DC_DT')

            ## Step by step calculation (12 steps) of Wax Loop algorithm :
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

            ## Updating dfOutputs entry of current iteration :
            self.Save_outputs()
            
        self.dfOutputs.index.name = 'TIME'

    def Calc(self,func):

        if func=='VO':
            ## Using given mo, we first calculate Qo :
            self.Val['QO'] = self.Val['MO'] / self.Val['RHOO']
            ## Then calculating Vo, using area of circle [A = π x (dw/2)²] of the current iteration :
            self.Val['VO'] = self.Val['QO'] / (math.pi*math.pow(self.Val['DW']/2,2))

        elif func=='DELD':
            self.Val['DELD'] = 0.5*(self.Val['DI'] - self.Val['DW'])

        elif func=='NSR':
            self.Val['NSR'] = (self.Val['RHOOW'] * self.Val['VO'] * self.Val['DELD']) / self.Val['UOW']

        elif func=='REOW':
            self.Val['REOW'] = (self.Val['RHOOW'] * self.Val['VO'] * self.Val['DW']) / self.Val['UOW']

        elif func=='FO':
            self.Val['FO'] = 100*(1-((self.Val['REOW']**0.15)/8))

        elif func=='FW':
            self.Val['FW'] = 1-(self.Val['FO']/100)

        elif func=='PY1':
            self.Val['PY1'] = self.Val['C1'] / (1-(self.Val['FO']/100))

        elif func=='PY2':
            self.Val['PY2'] = self.Val['C2'] * (self.Val['NSR']**self.Val['C3'])

        elif func=='MVWW':
            ## Converting ρww from kg/m³ to g/cm³ :
            RHOWW = self.Val['RHOWW'] * 0.001
            self.Val['MVWW'] = self.Val['MWWW'] / (RHOWW)
            
        elif func=='DOW':
            ## Converting Tw from °C to K :
            TW = self.Val['TW'] + 273.15
            ## Converting μow from Pa.s to mPa.s :
            UOW = self.Val['UOW'] * 1000

            if self.Val['DOWMethod']=='Wilke-Chang':
                self.Val['DOW'] = 7.4E-12 * ((TW*math.pow(self.Val['MWOW'],0.5))/(UOW*math.pow(self.Val['MVWW'],0.6)))
            elif self.Val['DOWMethod']=='Hayduk-Minhass':
                self.Val['DOW'] = 13.3E-12 * ((math.pow(TW,1.47)*math.pow(UOW,(10.2/self.Val['MVWW'])-0.791))/math.pow(self.Val['MVWW'],0.71))

        elif func=='DDEL_DT':
            ## We incorporate also dt in seconds (from minutes) since the expected output is in mm, not mm/s
            DDEL_DT = (self.Val['PY1']/(1+self.Val['PY2']))*self.Val['DOW']*(self.Val['DC_DT']*self.Val['DT_DR'])* (10*60)
            ## Converting dδ/dt from m to mm
            self.Val['DDEL_DT'] = DDEL_DT * 1000

        elif func=='DELTA':
            self.Val['DELTA'] = self.Val['DELTA_TMINUS1'] + (self.Val['DDEL_DT'])

    def Get(self, var):

        if var=='From Input Files':
            '''
            From TAB file :
                [1] Pressure table      Dictionary that maps to all 50 Pressure points.
                [2] Temperature table   Dictionary that maps to all 50 Temperature points.
                [3] TAB properties      Two-level dictionaries that maps property values at 
                                        each pressure and temperature point.
                                        [1] Liquid/oil Density. 
                                        [2] Liquid/oil Viscosity.

            From WAX file :
                [1] Pressure table      Dictionary that maps to all 30 Pressure points.
                [2] Temperature table   Dictionary that maps to all 30 Temperature points.
                [3] WAX properties      Two-level dictionaries that maps property values at 
                                        each pressure and temperature point.
                                        [1] Wax concentration. 
                                        [2] Wax density.
                                        [3] Liquid/oil molecular weight.
                                        [4] Wax molecular weight.

            From Excel file : Tw, dw, and dT/dr values at each simulation time index.
            '''
            self.Table['P_Table_TAB'], self.Table['T_Table_TAB'], self.Table['TAB_Properties'] = ccd.Get_File_Inputs(self.Files['tab'],'tab')
            self.Table['P_Table_WAX'], self.Table['T_Table_WAX'], self.Table['WAX_Properties'] = ccd.Get_File_Inputs(self.Files['wax'],'wax')
            self.dfInputs = ccd.Get_File_Inputs(self.Files['xlsx'],'xlsx')
        
        elif var=='PIO_TABIndex':
            self.Val['PIO_TABIndex'] = ccd.P_TEMP_Index(self.Table['P_Table_TAB'], self.Val['PIO'])
        
        elif var=='TOI_TABIndex':
            self.Val['TOI_TABIndex'] = ccd.P_TEMP_Index(self.Table['T_Table_TAB'], self.Val['TOI'])
        
        elif var=='RHOO':
            self.Val['RHOO'] = ccd.Get_Property(
                self.Val['PIO_TABIndex'], self.Val['TOI_TABIndex'], self.Table['TAB_Properties']['RHOOW']
            )
        
        elif var=='CWAXFEED':
            self.Val['CWAXFEED'] = sum(self.Table['WAX_Properties']['CWAXFEED'])

        elif var=='TW':
            self.Val['TW'] = self.dfInputs.loc[self.Val['TIME'],'Tw']

        elif var=='DW':
            ## Converting dw from mm to m :
            self.Val['DW'] = self.dfInputs.loc[self.Val['TIME'],'dw'] * 0.001

        elif var=='DT_DR':
            self.Val['DT_DR'] = self.dfInputs.loc[self.Val['TIME'],'dT/dr']

        elif var=='DELTA_TMINUS1':
            self.Val['DELTA_TMINUS1'] = self.Val['DELTA']

        elif var=='TW_TABIndex':
            self.Val['TW_TABIndex'] = ccd.P_TEMP_Index(self.Table['T_Table_TAB'], self.Val['TW'])

        elif var=='PIO_WAXIndex':
            self.Val['PIO_WAXIndex'] = ccd.P_TEMP_Index(self.Table['P_Table_WAX'], self.Val['PIO'])

        elif var=='TW_WAXIndex':
            self.Val['TW_WAXIndex'] = ccd.P_TEMP_Index(self.Table['T_Table_WAX'], self.Val['TW'])

        elif var=='RHOOW':
            self.Val['RHOOW'] = ccd.Get_Property(
                self.Val['PIO_TABIndex'], self.Val['TW_TABIndex'], self.Table['TAB_Properties']['RHOOW']
            )

        elif var=='UOW':
            self.Val['UOW'] =   ccd.Get_Property(
                self.Val['PIO_TABIndex'], self.Val['TW_TABIndex'], self.Table['TAB_Properties']['UOW']
            )

        elif var=='MWWW':
            self.Val['MWWW'] =  ccd.Get_Property(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['WAX_Properties']['MWWW']
            )

        elif var=='MWOW':
            self.Val['MWOW'] =  ccd.Get_Property(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['WAX_Properties']['MWOW']
            )

        elif var=='RHOWW':
            self.Val['RHOWW'] =  ccd.Get_Property(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['WAX_Properties']['RHOWW']
            )

        elif var=='DC_DT':
            self.Val['DC_DT'] = ccd.Find_DC_DT(
                self.Val['PIO_WAXIndex'], self.Val['TW_WAXIndex'], self.Table['T_Table_WAX'], 
                self.Table['WAX_Properties']['CWAX'], self.Val['CWAXFEED']
            )
        
    def Save_outputs(self):
        Unit = ccd.Abbreviations('Unit')
        Symbol = ccd.Abbreviations('Symbol')

        for col in Symbol.keys():
            if self.Val['Iteration']==1:
                self.dfOutputs.loc['min', Symbol[col]] = Unit[col]
            self.dfOutputs.loc[self.Val['TIME'], Symbol[col]] = ccd.round_sig(self.Val[col],5)
