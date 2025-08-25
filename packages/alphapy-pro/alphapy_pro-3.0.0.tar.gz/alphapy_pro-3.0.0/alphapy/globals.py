################################################################################
#
# Package   : AlphaPy
# Module    : globals
# Created   : July 11, 2013
#
# Copyright 2022 ScottFree Analytics LLC
# Mark Conway & Robert D. Scott II
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################


#
# Imports
#

from enum import Enum, unique


#
# Global Variables
#


#
# Delimiters
#

BSEP = ' '
CSEP = ':'
ESEP = '='
PSEP = '.'
SSEP = '/'
USEP = '_'
LOFF = '['
ROFF = ']'
CARET = '^'
ATSIGN = '@'


#
# Numerical Constants
#

Q1 = 0.25
Q2 = 0.50
Q3 = 0.75


#
# String Constants
#

NULLTEXT = 'NULLTEXT'
WILDCARD = '*'


#
# Dictionaries
#

SUBJECTS = ['crypto', 'etf', 'forex', 'future', 'index', 'option', 'stock']


#
# Pandas Time Offset Aliases
#

PD_INTRADAY_OFFSETS = ['H', 'T', 'min', 'S', 'L', 'ms', 'U', 'us', 'N']
PD_DAILY_OFFSETS = ['D', 'W', 'M', 'Q', 'A']


#
# Encoder Types
#

@unique
class Encoders(Enum):
    """AlphaPy Encoders.

    These are the encoders used in AlphaPy, as configured in the
    ``model.yml`` file (features:encoding:type) You can learn more
    about encoders here [ENC]_.

    .. [ENC] https://github.com/scikit-learn-contrib/categorical-encoding

    """
    backdiff = 1
    basen = 2
    binary = 3
    catboost = 4
    hashing = 5
    helmert = 6
    jstein = 7
    leaveone = 8
    mestimate = 9
    onehot = 10
    ordinal = 11
    polynomial = 12
    sum = 13
    target = 14
    woe = 15


#
# Model Types
#

@unique
class ModelType(Enum):
    """AlphaPy Model Types.

    .. note:: Multiclass Classification ``multiclass`` is not yet
       implemented.

    """
    classification = 1
    ranking = 2
    multiclass = 3
    regression = 4
    system = 5


#
# Objective Functions
#

@unique
class Objective(Enum):
    """Scoring Function Objectives.

    Best model selection is based on the scoring or Objective
    function, which must be either maximized or minimized. For
    example, ``roc_auc`` is maximized, while ``neg_log_loss``
    is minimized.

    """
    maximize = 1
    minimize = 2


#
# Bar Types
#

@unique
class BarType(Enum):
    """Bar Types.

    Bar Types for running models, usually translated from a normal OHLC bar to a
    weighted bar based on volume, dollar amount, etc.

    """
    time = 1
    dollar = 2
    heikinashi = 3


#
# Class Orders
#

class Orders:
    """System Order Types.

    Attributes
    ----------
    le : str
        long entry
    se : str
        short entry
    lx : str
        long exit
    sx : str
        short exit
    lh : str
        long exit at the end of the holding period
    sh : str
        short exit at the end of the holding period

    """
    le = 'le'
    se = 'se'
    lx = 'lx'
    sx = 'sx'
    lh = 'lh'
    sh = 'sh'


#
# Partition Types
#

@unique
class Partition(Enum):
    """AlphaPy Partitions.

    """
    train = 1
    test = 2


#
# Datasets
#

datasets = {Partition.train    : 'train',
            Partition.test     : 'test'}


#
# Pivot Types
#

@unique
class PivotType(Enum):
    """Pivot Types.

    """
    PivotHigh = "High"
    PivotLow = "Low"


#
# Scaler Types
#

@unique
class Scalers(Enum):
    """AlphaPy Scalers.

    These are the scaling methods used in AlphaPy, as configured in the
    ``model.yml`` file (features:scaling:type) You can learn more about
    feature scaling here [SCALE]_.

    .. [SCALE] http://scikit-learn.org/stable/modules/preprocessing.html

    """
    minmax = 1
    standard = 2
