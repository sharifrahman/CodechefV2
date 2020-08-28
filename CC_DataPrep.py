import math
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from printandsave import printnsave

def Abbreviations(handle):
    Description = {
        'DI' : 'Initial oil pipe diameter',
        'DW' : 'Effective oil pipe diameter',
        'PIO' : 'Inlet pressure of oil',
        'TOI' : 'Inlet temperature of oil',
        'QO' : 'Volumetric flow rate of oil',
        'MO' : 'Mass flow rate of oil',
        'RHOO' : 'Density of (liquid) oil at Toi',
        'RHOOW' : 'Density of (liquid) oil at Tw',
        'RHOWW' : 'Density of wax at Tw',
        'UOW' : 'Viscosity of (liquid) oil at Tw',
        'VO' : 'Velocity of oil',
        'TW' : 'Wall or Oil/wax interface temperature',
        'DELD' : '(Guessed) Thickness of wax deposit layer',
        'NSR' : 'Reynold number of oil within deposit layer (evaluated at Tw)',
        'REOW' : 'Reynold number of oil (evaluated at Tw)',
        'FO' : 'Percentage (weight) of oil in the deposit',
        'FW' : 'Percentage (weight) of solid wax in the deposit',
        'PY1' : '',
        'PY2' : '',
        'DOW' : 'Diffusion rate of wax',
        'DT_DR' : 'Temperature difference at pipe wall or oil/wax interface',
        'MVWW' : 'Molar volume of wax',
        'MWWW' : 'Molecular weight of wax at Tw',
        'MWOW' : 'Molecular weight of (Liquid) oil at Tw',
        'TIME' : 'Simulation time',
        'CWAXFEED' : 'Concentration of total Wax in Feed',
        'DC_DT' : 'Slope of wax percipitation curve at Tw',
        'DDEL_DT' : 'Incremental increase of thickness of wax deposit layer',
        'DELTA' : 'Total thickness of wax deposit layer'
    }
    Unit = {
        'DI' : 'm',
        'DW' : 'm',
        'PIO' : 'Pa',
        'TOI' : '°C',
        'QO' : 'm³/s',
        'MO' : 'kg/s',
        'RHOO' : 'kg/m³',
        'RHOOW' : 'kg/m³',
        'RHOWW' : 'kg/m³',
        'UOW' : 'Pa.s',
        'VO' : 'm/s',
        'TW' : 'degC',
        'DELD' : 'm',
        'NSR' : '',
        'REOW' : '',
        'FO' : '%',
        'FW' : 'Frac.',
        'PY1' : '',
        'PY2' : '',
        'DOW' : 'm²/s',
        'DT_DR' : 'K/m',
        'MWWW' : 'g/mol',
        'MWOW' : 'g/mol',
        'MVWW' : 'cm³/mol',
        'TIME' : 'min',
        'CWAXFEED' : 'mol/mol',
        'DC_DT' : '',
        'DDEL_DT' : 'mm/s',
        'DELTA' : 'mm'
    }

    Equation = {
        'VO' : 'Qo = mo / RHOo \nVo = Qo / (pi x di/2)^2',
        'DELD' : 'DELd = 0.5 x (di-dw)',
        'NSR' : 'Nsr = (RHOow x Vo x DELd)/UOW',
        'REOW' : 'Reow = (RHOow x Vo x DELd)/UOW',
        'FO' : 'Fo = 100 x (1-((Reow ^ 0.15)/8))',
        'FW' : 'Fw = 100 x (1-((Reow ^ 0.15)/8))',
        'PY1' : 'PY1 = C1 / (1-(Fo/100))',
        'PY2' : 'PY2 = C2 x (Nsr ^ C3)',
        'DOW' : '',
        'MVWW' : 'MVww = MWww / RHOww',
        'DDEL_DT' : 'dDEL/dt = (PY1 / (1+PY2)) x Dow x (dC/dT x dT/dr)',
        'DELTA' : 'DELTA = DELt-1 + (dDEL/dt x dt)'
    }

    Symbol = {
        'TIME' : 'Time',
        'TW' : 'Tw',
        'DW' : 'dw',
        'DT_DR' : 'dT/dr',
        'RHOO' : 'ρo',
        'QO' : 'Qo',
        'VO' : 'Vo',
        'DELD' : 'δd',
        'RHOOW' : 'ρow',
        'UOW' : 'μow',
        'REOW' : 'Reow',
        'FO' : 'Fo',
        'FW' : 'Fw',
        'NSR' : 'Nsr',
        'MWWW' : 'MWww',
        'RHOWW' : 'ρww',
        'MVWW' : 'MVww',
        'PY1' : 'π1',
        'PY2' : 'π2',
        'DOW' : 'Dow',
        'DC_DT' : 'dC/dT',
        'DDEL_DT' : 'dδ/dt',
        'DELTA' : 'δ'
    }


    if handle=='Description':
        return Description
    elif handle=='Unit':
        return Unit
    elif handle=='Equation':
        return Equation
    elif handle=='Symbol':
        return Symbol

def Get_File_Inputs(filepath, filetype):
    if filetype=='xlsx':
        dfIO = pd.read_excel(filepath, index_col=0, skiprows=[1])
        return dfIO
    else:
        TextLines = LoadTextFiles(filepath)
        if filetype=='tab':
            P, TEMP = LookFor_TAB_PT(TextLines)
            Pointer = {
                PROP : i+1 
                for i, Line in enumerate(TextLines) 
                for PROP in ['DENSITY','VISCOSITY','HEAT CAPACITY','THERMAL CONDUCTIVITY'] 
                if 'LIQUID '+PROP in Line
            }
            RHO = LookFor_TAB_Property(TextLines, P, Pointer['DENSITY'])
            U = LookFor_TAB_Property(TextLines, P, Pointer['VISCOSITY'])
            # CP = LookFor_TAB_Property(TextLines, P, Pointer['HEAT CAPACITY'])
            # KO = LookFor_TAB_Property(TextLines, P, Pointer['THERMAL CONDUCTIVITY'])
            return P, TEMP, {'RHO LIQ':RHO, 'U LIQ':U}
        elif filetype=='wax':
            Pointer = [
                i
                for i, Line in enumerate(TextLines)
                if '!Pressure Point No.' in Line
            ]
            P, TEMP = LookFor_WAX_PT(TextLines, Pointer)
            PropertiesTable = LookForCC_WAX_Properties(TextLines, Pointer)
            ComponentProperties = LookFor_WAX_Comp_Properties(TextLines)

            for CP in ComponentProperties:
                PropertiesTable[CP] = ComponentProperties[CP]

            return P, TEMP, PropertiesTable

def LoadTextFiles(filepath):
    f = open(filepath, 'r')
    TextLines = []
    for x in f:
        TextLines.append(x)
    f.close()
    return TextLines

def LookFor_TAB_PT(TextLines):
    PTLinePointer = {
        'P': np.arange(2,12),
        'TEMP': np.arange(12,22),
    }
    PT = {}
    for Property in PTLinePointer.keys():
        PropertyPoints, Count = {}, 1
        for n in PTLinePointer[Property]:
            for Point in SplitTabLine(TextLines[n]):
                PropertyPoints[Count] = Point
                Count += 1
        PT[Property] = PropertyPoints
    return PT['P'], PT['TEMP']

def LookFor_WAX_PT(TextLines, Pointer):
    P, TEMP = {}, {}
    for i, point in enumerate(Pointer):
        P[i+1] = float(TextLines[point+1])
        if i==0:
            for j in range(30):
                TEMP[j+1] = float(TextLines[point+3+(9*j)])
    return P, TEMP

def LookFor_WAX_Comp_Properties(TextLines):
    Property_pointer = {
        # 'CNAME' : np.arange(8,12), 
        'MW WAX Components' : np.arange(13,18), 
        'RHO WAX Components' : np.arange(19,24), 
        # 'WAX HEAT OF MELTING' : np.arange(25,30), 
        'CWAXFEED' : np.arange(31,39)        
    }

    PropertiesTable = {}
    for Property in Property_pointer:
        TableByComponents = {}
        Count = 1
        for Line in Property_pointer[Property]:
            for Point in SplitTabLine(TextLines[Line]):
                TableByComponents[Count] = Point
                Count += 1
        PropertiesTable[Property] = TableByComponents
    
    return PropertiesTable

def SplitTabLine(TextLine):
    Arr = [float(A) for A in TextLine.split()]
    return Arr

def LookFor_TAB_Property(TextLines, PressurePoints, Pointer):
    Line_init, PropertyTable = Pointer, {}
    for i in range(50): # 50 Pressure points
        PropertyTableByTEMP, Count = {}, 1
        for n in np.arange(Line_init, Line_init+10):
            for value in SplitTabLine(TextLines[n]):
                PropertyTableByTEMP[Count] = value
                Count += 1
        PropertyTable[i+1] = PropertyTableByTEMP
        Line_init += 10
    return PropertyTable

def LookForCC_WAX_Properties(TextLines, Pointers):
    Property_pointer = {
        'CONCS WAX' : np.arange(0,47), 
        'RHO WAX' : 47, 
        # 'GAS MW' : 48,
        'MW LIQ' : 49, 
        'MW WAX' : 50 #,
        # 'WAX ENTALPY' : 51,
        # 'WAX HEAT CAPACITY' : 52,
        # 'THERM COND' : 53
    }

    Properties = {}
    for i in range(30):
        PropertiesByTEMP = {}
        Line_init = Pointers[i] # First line of Pressure point i_index
        for j in range(30):
            Linenum = Line_init+4+(9*j) # First line of data for P-i_index TEMP-j_index
            Values_ij, PropTable_ij = [], {}
            for n in np.arange(Linenum, Linenum+8):
                for value in SplitTabLine(TextLines[n]):
                    Values_ij.append(value)
            for Property in Property_pointer:
                Value_index = Property_pointer[Property]
                if isinstance(Value_index,int):
                    PropTable_ij[Property] = Values_ij[Value_index]
                else:
                    PropTable_ij[Property] = [Values_ij[v] for v in Value_index]
            PropertiesByTEMP[j+1] = PropTable_ij
        Properties[i+1] = PropertiesByTEMP

    PropertiesTable = {}
    for Property in Property_pointer:
        TableByP = {}
        for i in range(30):
            TableByTEMP = {}
            for j in range(30):
                TableByTEMP[j+1] = Properties[i+1][j+1][Property]
            TableByP[i+1] = TableByTEMP
        PropertiesTable[Property] = TableByP

    return PropertiesTable

def Find_Nearest(Ref, Value):
    Index_exact = [i for i in Ref if Ref[i]==Value]
    if Index_exact:
        return [Index_exact[0], True]
    else:
        Upperbound = np.argsort([Ref[i]-Value if Ref[i]-Value>0 else 1E8 for i in Ref])[0]
        Lowerbound = np.argsort([Value-Ref[i] if Value-Ref[i]>0 else 1E8 for i in Ref])[0]
        Nearest = [
            index 
            for j in [Lowerbound, Upperbound] 
            for i, index in enumerate(Ref) 
            if j==i
        ]
        Mid_Index = ((Value - Ref[Nearest[0]])/(Ref[Nearest[1]]-Ref[Nearest[0]])) + Nearest[0]
        return [Mid_Index, False]

def Get_Property(P_Index, TEMP_Index, PropertyTable):
    [PIndex, PExact] = P_Index
    [TIndex, TExact] = TEMP_Index

    if PExact:
        if TExact:
            Property = PropertyTable[PIndex][TIndex]
        else:
            PropertyTable_SingleP = PropertyTable[PIndex]
            Property = Interp_Property(PropertyTable_SingleP, TIndex)
    else:
        if TExact:
            PropertyTable_SingleT = {P:PropertyTable[P][TIndex] for P in PropertyTable}
            Property = Interp_Property(PropertyTable_SingleT, PIndex)
        else:
            Property = Interp_Property(PropertyTable, [PIndex, TIndex], Single=False)
    return Property

def Interp_Property(PropertyTable, Index, Single=True):
    if Single:
        Lower_bound = PropertyTable[int(np.floor(Index))]
        Upper_bound = PropertyTable[int(np.ceil(Index))]
        Ratio = Index - np.floor(Index)
        Property = (Ratio * (Upper_bound - Lower_bound)) + Lower_bound
        # printnsave('./', 'Lower bound = {}, Upper bound = {}, Ratio = {}, Interp Property = {}'.format(
        #     Lower_bound, Upper_bound, Ratio, Property
        # ))
    else:
        [PIndex, TIndex] = Index
        Points = [
            [P,T] 
            for P in [np.floor(PIndex), np.ceil(PIndex)] 
            for T in [np.floor(TIndex), np.ceil(TIndex)]
        ]
        Values = [
            PropertyTable[P][T] 
            for P in [np.floor(PIndex), np.ceil(PIndex)] 
            for T in [np.floor(TIndex), np.ceil(TIndex)]
        ]
        Xi = ([PIndex, TIndex])
        Property = griddata(Points, Values, Xi, method='linear')
    return Property

def Find_DC_DT(P_Index, TEMP_Index, TEMP_Table, CWAX_Table, CWAX_Feed):
    
    [PIndex, PExact] = P_Index
    [TIndex, TExact] = TEMP_Index

    # printnsave('./', '\nGetting dC/dT')
    # printnsave('./', 'P Index : {} [{}], T Index : {} [{}]'.format(PIndex, PExact, TIndex, TExact))

    if TExact:
        LowerT = TIndex-1 if TIndex-1>0 else 0
        UpperT = TIndex+1 if TIndex+1<30 else 30
    else:
        LowerT = int(np.floor(TIndex))
        UpperT = int(np.ceil(TIndex))

    # printnsave('./', 'LowerT : {}, UpperT : {}'.format(LowerT, UpperT))

    if PExact:
        CWAX_LowerT = sum(CWAX_Table[PIndex][LowerT])
        CWAX_UpperT = sum(CWAX_Table[PIndex][UpperT])
    else:
        CWAXTable_LowerT = {P:sum(CWAX_Table[P][LowerT]) for P in CWAX_Table}
        CWAXTable_UpperT = {P:sum(CWAX_Table[P][UpperT]) for P in CWAX_Table}
        CWAX_LowerT = Interp_Property(CWAXTable_LowerT, PIndex)
        CWAX_UpperT = Interp_Property(CWAXTable_UpperT, PIndex)

    CWaxPercipitate_Lower = CWAX_Feed - CWAX_LowerT
    CWaxPercipitate_Upper = CWAX_Feed - CWAX_UpperT

    TEMP_Lower = TEMP_Table[LowerT]
    TEMP_Upper = TEMP_Table[UpperT]
    DC_DT = abs((CWaxPercipitate_Upper - CWaxPercipitate_Lower) / (TEMP_Lower - TEMP_Upper))

    # printnsave('./', 'CWAX_LowerT : {}, CWAX_UpperT : {}'.format(CWAX_LowerT, CWAX_UpperT))
    # printnsave('./', 'TEMP_Lower : {}, TEMP_Upper : {}'.format(TEMP_Lower, TEMP_Upper))
    # printnsave('./', 'DC_DT : {}'.format(DC_DT))

    return DC_DT

def round_sig(x, sig=3):
    try:
        return np.round(x, sig-int(math.floor(math.log10(abs(x))))-1)
    except:
        return np.round(x, sig)
    

