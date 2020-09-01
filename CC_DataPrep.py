import math
import numpy as np
import pandas as pd
from scipy.interpolate import griddata

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
        'DDEL_DT' : 'mm',
        'DELTA' : 'mm'
    }

    Equation = {
        'VO' : 'Qo = mo / ρo \nVo = Qo / (π x dw/2)²',
        'DELD' : 'δd = 0.5 x (di-dw)',
        'NSR' : 'Nsr = (ρow x Vo x δd)/μow',
        'REOW' : 'Reow = (ρow x Vo x δd)/μow',
        'FO' : 'Fo = 100 x (1-((Reow ^ 0.15)/8))',
        'FW' : 'Fw = 1 - Fo/100',
        'PY1' : 'π1 = C1 / (1-(Fo/100))',
        'PY2' : 'π2 = C2 x (Nsr ^ C3)',
        'DOW' : '',
        'MVWW' : 'MVww = MWww / ρww',
        'DDEL_DT' : 'dδ/dt = (π1 / (1+π2)) x Dow x (dC/dT x dT/dr)',
        'DELTA' : 'δ = δt-1 + (dδ/dt x dt)'
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
        ## We use pandas read_excel straight forward for excel input file :
        dfIO = pd.read_excel(filepath, index_col=0, skiprows=[1])
        return dfIO
    else:
        ## For TAB and WAX files, LoadTextFiles function to convert textfile lines into list :
        TextLines = LoadTextFiles(filepath)
        ## LookFor_P_TEMP function to obtain Pressure and Temperature tables :
        P, TEMP = LookFor_P_TEMP(TextLines, filetype)
        ## LookFor_Properties function to obtain corresponding TAB or WAX properties :
        PropertiesTable = LookFor_Properties(TextLines, filetype)
        return P, TEMP, PropertiesTable

def LoadTextFiles(filepath):
    f = open(filepath, 'r')
    TextLines = []
    for x in f:
        TextLines.append(x)
    f.close()
    return TextLines

def SplitTextLine(TextLine):
    Arr = [float(A) for A in TextLine.split()]
    return Arr

def LookFor_P_TEMP(TextLines, File):
    if File == 'tab':
        '''
        In TAB file, Pressure points located from Line 3 to 11, 
        while Temperature points located from Line 12 to 22.
        Each line contains 5 points separated by \t. 
        We use SplitTextLine to split line into list array of 5.

        Output: Two (2) sets of Dictionaries that maps pressure and
                temperature points from 1 to 50.
        '''
        ## Note that python numbering starts at 0
        Pointer = {
            'P': np.arange(2,12),
            'TEMP': np.arange(12,22),
        }
        PT = {}
        for Property in Pointer.keys():
            PropertyPoints, Count = {}, 1
            for n in Pointer[Property]:
                for Point in SplitTextLine(TextLines[n]):
                    PropertyPoints[Count] = Point
                    Count += 1
            PT[Property] = PropertyPoints
        return PT['P'], PT['TEMP']

    elif File == 'wax':
        '''
        In WAX file, 
        Pressure points located at every 1 line after '!Pressure Point No.'
        Followed by 30 temperature points (j) located at [3+(9*j)].

        Output: Two (2) sets of Dictionaries that maps pressure and
                temperature points from 1 to 30.
        '''
        Pointer = [
            i
            for i, Line in enumerate(TextLines)
            if '!Pressure Point No.' in Line
        ]
        P, TEMP = {}, {}
        for i, point in enumerate(Pointer):
            P[i+1] = float(TextLines[point+1])
            if i==0:
                for j in range(30):
                    TEMP[j+1] = float(TextLines[point+3+(9*j)])
        return P, TEMP

def LookFor_Properties(TextLines, File):
    if File == 'tab':
        '''
        In TAB file,
        We locate starting line (pointer) of a single TAB property by finding lines with
        the exact keyword i.e. LIQUID DENSITY.
        All 50 pressure points located at every 10 text lines after the first one, which
        contains the corresponding property values at 50 different temperature points.
        '''
        Property_pointer = {
            PROP : i+1 
            for i, Line in enumerate(TextLines) 
            for PROP in [
                'DENSITY','VISCOSITY'#,
                # 'HEAT CAPACITY','THERMAL CONDUCTIVITY'
            ] 
            if 'LIQUID '+PROP in Line
        }
        Abbrev = {
            'DENSITY' : 'RHOOW',
            'VISCOSITY' : 'UOW'#,
            # 'HEAT CAPACITY' : '',
            # 'THERMAL CONDUCTIVITY' : ''
        }
        '''
        We then create 3 tiers of nested dictionaries:
        T1 (Tier 1) : Dictionary of all TAB properties.
        T2 (Tier 2) : Dictionary of single TAB property of all 50 pressure points.
        T3 (Tier 3) : Dictionary of single TAB property of all 50 temperature points 
                    in a single pressure point.
        '''
        T1 = {}
        for PROP in Property_pointer:
            Line_init, T2 = Property_pointer[PROP], {}
            for i in range(50):
                T3, Count = {}, 1
                for n in np.arange(Line_init, Line_init+10):
                    for value in SplitTextLine(TextLines[n]):
                        T3[Count] = value
                        Count += 1
                T2[i+1] = T3
                Line_init += 10
            T1[Abbrev[PROP]] = T2
        return T1

    elif File == 'wax':
        '''
        In WAX file,
        We locate starting line (segment pointer) all 30 pressure points by finding 
        lines that start with '!Pressure Point No.'
        All 30 corresponding temperature points of a single pressure point located at 
        every 9 text lines after the first one.
        Under a single temperature point, we then locate the corresponding WAX properties
        indices that are required for Level 1:
            [1] Wax Concs   Index 0 to 46
            [2] Dens        Index 47
            [3] Liq MW      Index 49
            [4] Wax MW      Index 50
        We listed down but commented the other properties for future reference.
        '''
        Segment_pointer = [
            i
            for i, Line in enumerate(TextLines)
            if '!Pressure Point No.' in Line
        ]
        Property_pointer = {
            'Wax Concs' : np.arange(0,47), 
            'Dens' : 47, 
            # 'Gas MW' : 48,
            'Liq MW' : 49, 
            'Wax MW' : 50 #,
            # 'Hwax' : 51,
            # 'Cpwax' : 52,
            # 'Therm Cond' : 53
        }
        Abbrev = {
            'Wax Concs' : 'CWAX', 
            'Dens' : 'RHOWW', 
            # 'Gas MW' : '',
            'Liq MW' : 'MWOW', 
            'Wax MW' : 'MWWW' #,
            # 'Hwax' : '',
            # 'Cpwax' : '',
            # 'Therm Cond' : ''
        }

        '''
        We then create 3 tiers of nested dictionaries:
        T1 (Tier 1) : Dictionary of all WAX properties for all 50 pressure points.
        T2 (Tier 2) : Dictionary of all WAX properties for all 50 temperature points 
                    in a single pressure point.
        T3 (Tier 3) : Dictionary of single WAX property value at given pressure and
                    temperature point.
        '''
        T1 = {}
        for i in range(30):
            T2 = {}
            Line_init = Segment_pointer[i]
            for j in range(30):
                Linenum = Line_init+4+(9*j)
                Values_ij, T3 = [], {}
                for n in np.arange(Linenum, Linenum+8):
                    for value in SplitTextLine(TextLines[n]):
                        Values_ij.append(value)
                for PROP in Property_pointer:
                    Value_index = Property_pointer[PROP]
                    if isinstance(Value_index,int):
                        T3[PROP] = Values_ij[Value_index]
                    else:
                    # 'Wax Concs' stored as list of 47 values. Others are integer.
                        T3[PROP] = [Values_ij[v] for v in Value_index]
                T2[j+1] = T3
            T1[i+1] = T2

        '''
        Rearranging the nested dictionaries, to follow previous (TAB) format.
        N1 (New Tier 1) : Dictionary of all WAX properties.
        N2 (New Tier 2) : Dictionary of single WAX property of all 50 pressure points.
        N3 (New Tier 3) : Dictionary of single WAX property of all 50 temperature points 
                        in a single pressure point.
        '''
        N1 = {}
        for PROP in Property_pointer:
            N2 = {}
            for i in range(30):
                N3 = {}
                for j in range(30):
                    N3[j+1] = T1[i+1][j+1][PROP]
                N2[i+1] = N3
            N1[Abbrev[PROP]] = N2

        '''
        In the same WAX file, we can find several WAX properties related to wax components,
        which are not bounded to any pressure or temperature point.
        For Level 1, only CWAXFEED is required.
        We listed down but commented the other properties for future reference.
        '''
        Property_pointer = {
            # 'Names of wax components' : np.arange(8,12), 
            # 'MW of wax components' : np.arange(13,18), 
            # 'Density of wax components' : np.arange(19,24), 
            # 'Heat of melting of wax components' : np.arange(25,30), 
            'Concentration of wax components in feed' : np.arange(31,39)        
        }
        Abbrev = {
            # 'Names of wax components' : '', 
            # 'MW of wax components' : '', 
            # 'Density of wax components' : '', 
            # 'Heat of melting of wax components' : '', 
            'Concentration of wax components in feed' : 'CWAXFEED'       
        }
        '''
        Addition to previous N1, we created 2nd tier of dictionary :
        A2 (Addition Tier 2) : Dictionary of a single WAX components property.
        '''
        for PROP in Property_pointer:
            A2 = {}
            Count = 1
            for Line in Property_pointer[PROP]:
                for Point in SplitTextLine(TextLines[Line]):
                    A2[Count] = Point
                    Count += 1
            N1[Abbrev[PROP]] = A2
        return N1

def P_TEMP_Index(Table, Value):
    '''
    This function converts Pressure or Temperature value into index number of the reference table.
    Function will return the exact index and True if the value provided equals to any one of 
    pressure/temperature points.
    Else, interpolated 'index' will be calculated using linear interpolation, and marked as False. 
    The boolean (True/False) output will be used later when getting corresponding properties.
    '''
    Index_exact = [i for i in Table if Table[i]==Value]
    if Index_exact:
        return [Index_exact[0], True]
    else:
        Upperbound = np.argsort([Table[i]-Value if Table[i]-Value>0 else 1E8 for i in Table])[0]
        Lowerbound = np.argsort([Value-Table[i] if Value-Table[i]>0 else 1E8 for i in Table])[0]
        Nearest = [
            index 
            for j in [Lowerbound, Upperbound] 
            for i, index in enumerate(Table) 
            if j==i
        ]
        Index_interp = ((Value - Table[Nearest[0]])/(Table[Nearest[1]]-Table[Nearest[0]])) + Nearest[0]
        return [Index_interp, False]

def Get_Property(P_Index, TEMP_Index, PropertyTable):
    '''
    In previous function, we managed to return the P or TEMP 'index' which consists of:
    [1] PIndex or TIndex : The exact or interpolated 'index'
    [2] PExact or TExact : True = exact, False = interpolated
    If both P and TEMP are True, then we can directly use them to obtain corresponding property
    value from the nested dictionaries. However if any one is False, then we need to interpolate.
    '''
    [PIndex, PExact] = P_Index
    [TIndex, TExact] = TEMP_Index

    if PExact:
        if TExact:
            Value = PropertyTable[PIndex][TIndex]
        else:
            Value = Interp_Property(PropertyTable[PIndex], TIndex)
    else:
        if TExact:
            ## Reformulate: a dictionary of single property for all pressure points in a single pressure point :
            PropertyTable_TIndex = {P:PropertyTable[P][TIndex] for P in PropertyTable}
            Value = Interp_Property(PropertyTable_TIndex, PIndex)
        else:
            Value = Interp_Property(PropertyTable, [PIndex, TIndex], Both=True)
    return Value

def Interp_Property(PropertyTable, Index, Both=False):
    '''
    If only one of P or TEMP is interpolated index, then we interpolate by simply using
    linear interpolation.
    If both of them are interpolated index, we use griddata to interpolate.
    '''
    if not Both:
        Lower_bound = PropertyTable[int(np.floor(Index))]
        Upper_bound = PropertyTable[int(np.ceil(Index))]
        Ratio = Index - np.floor(Index)
        Property = (Ratio * (Upper_bound - Lower_bound)) + Lower_bound
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

    if TExact:
        LowerT = TIndex-1 if TIndex-1>0 else 0
        UpperT = TIndex+1 if TIndex+1<30 else 30
    else:
        LowerT = int(np.floor(TIndex))
        UpperT = int(np.ceil(TIndex))

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

    return DC_DT

def round_sig(x, sig=3):
    if isinstance(x,np.ndarray):
        x = x[0]
    try:
        return np.round(x, sig-int(math.floor(math.log10(abs(x))))-1)
    except:
        return np.round(x, sig)
    

