"""MLFastFlow - packages for fast dataflow and workflow processing."""

__version__ = "0.2.6.2"

# Import core components
from mlfastflow.core import Flow

# Import sourcing functionality
import mlfastflow.sourcing as sourcing
from mlfastflow.sourcing import Sourcing

# Import fastKNN functionality  
import mlfastflow.fastKNN as fastKNN
from mlfastflow.fastKNN import fastKNN as fastKNNClass
 
# Import BigQueryClient
import mlfastflow.bigqueryclient as bigqueryclient
from mlfastflow.bigqueryclient import BigQueryClient
import mlfastflow.bigqueryclientpolars as bigqueryclientpolars
from mlfastflow.bigqueryclientpolars import BigQueryClientPolars

# Import utils module (functions accessible via utils.function_name)
import mlfastflow.utils as utils

# Import utility functions directly
from mlfastflow.utils import timer_decorator, concat_files, profile, csv2parquet

# Make these classes and modules available at the package level
__all__ = [
    'Flow',
    'bigqueryclient',  # module
    'BigQueryClient',  # class
    'BigQueryClientPolars',  # class
    'bigqueryclientpolars',  # module
    'Sourcing',        # module, the sourcing.py file
    'sourcing',        # class, the sourcing class in sourcing.py
    'FastKNN',         # module, the FastKNN.py file
    'fastKNN',         # class, the fastKNN class in FastKNN.py
    'utils',           # module
    'timer_decorator', # function
    'concat_files',    # function
    'profile',         # function
    'csv2parquet',     # function
]
