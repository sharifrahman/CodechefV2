import os
import math
import numpy as np
import pandas as pd
import CC_DataPrep as ccd

class Master():

    def __init__(
        self, Files, Alpha_input='Alpha w', PIO=101325
    ): 

        '''
        We implement different strategy for Level 2: Using Python Lambda

        Two (2) main instance variables:

            [1] Val         Dictionary that maps abbreviations to its corresponding values.

            [2] Table       Dictionary that maps Pressure, Temperature and corresponding Properties from 
                            TAB and WAX files.

         main class methods:

            [1] Alpha_switcher  
                - Switching between Alpha w and Alpha c

            [2] Alpha_W and Alpha_C         
                - Step by step equations under selected Alpha
            
            [3] Flow_switcher
                - Switching between Laminar and Turbulent flow
            
            [4] Calc
                - Switching between equations. All non-unique equations are placed here
                using python lambda function.

            [5] Get_Inputs
                - Extracting table and variable values from input files.
            
            [6] Get_Val
                - Acquiring variable values from:
                [1] TAB file table data.
                [2] Coolant excel file table data.
                [3] Inputs excel file input data at given simulation time index.

            [7] Save_outputs
                - Saving outputs in pandas dataframe
                - Final dataframe will be saved in ./output folder.
            
        '''
        ## Converting the user defined input file names as instance variable list :
        self.Files = Files

        ## Reading from the TAB and excel files :
        self.Get_Inputs()

        ## Creating dfOutput empty dataframe :
        self.dfOutputs = pd.DataFrame()

        ## Initiating Val dictionary key and value :
        self.Val = {'PIO':PIO}

        ## Starting the iterative calculation :
        for Iteration, Time in enumerate(self.dfInputs.index.values):
            self.Val['Iteration'] = Iteration + 1
            self.Val['TIME'] = Time
            self.Get_Val()
            self.Alpha_switcher(Alpha_input)

        self.dfOutputs.index.name = 'TIME'
        self.dfOutputs.to_excel('./output/Output DF Level 2 {}.xlsx'.format(Alpha_input))

    
    def Alpha_switcher(self, alpha_input):

        if alpha_input=='Alpha w':
            self.Alpha_W()

        elif alpha_input=='Alpha c':
            self.Alpha_C()
    
    def Alpha_W(self):

        self.Val['DH'] = self.Val['DI'] if self.Val['TIME']==0 else self.Val['DW']
        self.Val['UO/UOW'] = self.Calc('UO/UOW')(self.Val['UO'],self.Val['UOW'])
        self.Val['VO'] = self.Calc('V')(self.Val['MO'],self.Val['RHOO'],self.Val['DH'])
        self.Val['RE'] = self.Calc('RE')(self.Val['RHOOW'], self.Val['VO'], self.Val['DH'], self.Val['UOW'])
        self.Val['PR'] = self.Calc('PR')(self.Val['UOW'], self.Val['CPOW'], self.Val['KOW'])
        self.Val['L/DH'] = self.Calc('L/DH')(self.Val['L'], self.Val['DH'])
        self.Flow_switcher()
        self.Val['NUD'] = self.Val['NUFD']*(self.Val['UO/UOW']**0.11)
        self.Val['ALPHA W'] = self.Calc('ALPHA')(self.Val['NUD'], self.Val['DH'], self.Val['KOW'])
        self.Save_outputs('Alpha w')

    def Alpha_C(self):

        self.Val['DH'] = self.Val['DO']
        self.Val['VC'] = self.Calc('V')(self.Val['MC'],self.Val['RHOC'],self.Val['DH'])
        self.Val['RE'] = self.Calc('RE')(self.Val['RHOC'], self.Val['VC'], self.Val['DH'], self.Val['UC'])
        self.Val['PR'] = self.Calc('PR')(self.Val['UC'], self.Val['CPC'], self.Val['KC'])
        self.Val['L/DH'] = self.Calc('L/DH')(self.Val['L'], self.Val['DH'])
        self.Flow_switcher()
        self.Val['NUD'] = self.Val['NUFD']
        self.Val['ALPHA C'] = self.Calc('ALPHA')(self.Val['NUD'], self.Val['DH'], self.Val['KC'])
        self.Save_outputs('Alpha c')

    def Flow_switcher(self):

        if self.Val['RE']<=2300:
            self.Val['LE'] = self.Calc('LE')(self.Val['RE'], self.Val['DH'])
            Multiplier = self.Val['RE']*self.Val['PR']/self.Val['L/DH']
            if self.Val['L']>self.Val['LE']:
                self.Val['NUFD'] = 3.657 + (
                    (0.19*(Multiplier**0.8))/(1+0.117*(Multiplier**0.467))
                )
            else:
                if self.Val['PR']>=5:
                    self.Val['NUFD'] = 3.66 + ((0.0668*Multiplier)/(1+0.04*(Multiplier**(2/3))))
                else:
                    self.Val['NUFD'] = 1.86*(Multiplier**(1/3))

        else:
            self.Val['F'] = self.Calc('F')(self.Val['RE'])
            self.Val['NUFD1'] = self.Calc('NUFD1')(self.Val['F'], self.Val['RE'], self.Val['PR'])
            if self.Val['L/DH']>=60:
                self.Val['NUFD'] = self.Val['NUFD1']
            else:
                self.Val['NUFD'] = self.Val['NUFD1']*(2/(self.Val['L/DH']**(2/3)))


    def Calc(self, func):

        switcher = {
            'UO/UOW' : lambda uo,uow: uo/uow,
            'V' : lambda m,rho,dw: (m / rho)/(math.pi*(dw/2)**2),
            'RE' : lambda rho,v,dh,u: rho*v*dh/u,
            'PR' : lambda u,cp,k: u*cp/k,
            'L/DH' : lambda L,dh: L/dh,
            'F' : lambda re: (0.79*math.log(re)-1.64)**(-2),
            'NUFD1' : lambda f,re,pr: ((f/8)*(re-1000)*pr)/(1+12.7*((f/8)**0.5)*((pr**(2/3))-1)),
            'LE' : lambda re,dh: 0.06*re*dh,
            'ALPHA' : lambda nud,dh,k: nud*k/dh
        }
        return switcher.get(func, '-')

    def Get_Inputs(self):
        
        P, TEMP, Properties = ccd.Get_File_Inputs(self.Files['tab'],'tab')
        self.Table = {
            'P':P,
            'TEMP':TEMP,
            'Properties':Properties
        }
        self.dfInputs = ccd.Get_File_Inputs(self.Files['Inputs.xlsx'],'xlsx')
        dfCoolant = ccd.Get_File_Inputs(self.Files['Coolant.xlsx'],'xlsx')
        self.Coolant = {
            col :{
                i : dfCoolant.loc[i,col]
                for i in dfCoolant.index
            }
            for col in dfCoolant.columns
        }

    def Get_Val(self):

        for Var in self.dfInputs.columns:
            self.Val[Var] = self.dfInputs.loc[self.Val['TIME'],Var]

        self.Val['PIO Index'] = ccd.P_TEMP_Index(self.Table['P'], self.Val['PIO'])
        self.Val['TO Index'] = ccd.P_TEMP_Index(self.Table['TEMP'], self.Val['TO'])
        self.Val['TW Index'] = ccd.P_TEMP_Index(self.Table['TEMP'], self.Val['TW'])
        self.Val['TC Index'] = ccd.P_TEMP_Index(self.Coolant['TEMP'], self.Val['TC'])
        
        for Var in ['UO','RHOO']:
            self.Val[Var] = ccd.Get_Property(
                self.Val['PIO Index'], self.Val['TO Index'], self.Table['Properties'][Var+'W']
            )
        
        for Var in ['UOW', 'RHOOW', 'CPOW', 'KOW']:
            self.Val[Var] = ccd.Get_Property(
                self.Val['PIO Index'], self.Val['TW Index'], self.Table['Properties'][Var]
            )

        for Var in ['RHOC', 'UC', 'CPC', 'KC']:
            self.Val[Var] = ccd.Get_Coolant_Property(
                self.Val['TC Index'], self.Coolant[Var]
            )
    
    def Save_outputs(self, alpha_input):
        switcher = {
            'Alpha w': {'Unit':'UnitL2Aw', 'Symbol':'SymbolL2Aw'},
            'Alpha c': {'Unit':'UnitL2Ac', 'Symbol':'SymbolL2Ac'}
        }

        Unit = ccd.Abbreviations(switcher[alpha_input]['Unit'])
        Symbol = ccd.Abbreviations(switcher[alpha_input]['Symbol'])

        for col in Symbol.keys():
            if self.Val['Iteration']==1:
                self.dfOutputs.loc['min', Symbol[col]] = Unit[col]
            self.dfOutputs.loc[self.Val['TIME'], Symbol[col]] = ccd.round_sig(self.Val[col],5)


if __name__ == '__main__':
    
    Files = {
        'tab':'./Files/Dead Oil - Dulang 44 to 35C - OLGA tab - fixed format.tab',
        'Inputs.xlsx':'./Files/Dataset Level 2 Inputs.xlsx',
        'Coolant.xlsx':'./Files/Dataset Level 2 Coolant.xlsx'
    }
    Master(Files)