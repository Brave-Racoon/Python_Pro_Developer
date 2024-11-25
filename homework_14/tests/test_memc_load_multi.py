import pytest
from unittest.mock import patch, MagicMock, call
import gzip
import logging
from multiprocessing import Pool, cpu_count
from threading import Thread
import glob
from optparse import OptionParser
import sys
import appsinstalled_pb2

from memc_load_multi import process_file, main, prototest


# Mock dependencies
@patch('memc_load_multi.gzip.open')
@patch('memc_load_multi.Pool')
@patch('memc_load_multi.cpu_count')
@patch('memc_load_multi.process_line')
@patch('memc_load_multi.dot_rename')
def test_process_file(mock_dot_rename, mock_process_line, mock_cpu_count, mock_Pool, mock_gzip_open):
    # Mock gzip.open context manager
    mock_file = MagicMock()
    mock_file.readlines.return_value = [
        "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23",
        "gaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    ]
    mock_gzip_open.return_value.__enter__.return_value = mock_file
    mock_gzip_open.return_value.__exit__.return_value = False

    mock_cpu_count.return_value = 4
    mock_process_line.side_effect = [True, False]  # Simulate processing results

    # Mock Pool context manager
    mock_pool = MagicMock()
    mock_Pool.return_value.__enter__.return_value = mock_pool
    mock_Pool.return_value.__exit__.return_value = False
    mock_pool.starmap.return_value = [True, False]  # Simulate the results of starmap

    process_file('test_file.gz', {'idfa': '127.0.0.1:33013', 'gaid': '127.0.0.1:33014'}, False)

    # Assertions
    mock_dot_rename.assert_called_once_with('test_file.gz')


@patch('memc_load_multi.Thread')
@patch('memc_load_multi.glob.iglob')
def test_main(mock_iglob, mock_Thread):
    # Mock glob.iglob to return a list of filenames
    mock_iglob.return_value = ['file1.gz', 'file2.gz']

    # Mock Thread class
    mock_thread = MagicMock()
    mock_Thread.return_value = mock_thread

    # Create mock options
    options = MagicMock()
    options.idfa = '127.0.0.1:33013'
    options.gaid = '127.0.0.1:33014'
    options.adid = '127.0.0.1:33015'
    options.dvid = '127.0.0.1:33016'
    options.dry = False
    options.pattern = '/data/appsinstalled/*.tsv.gz'

    # Call main function
    main(options)

    # Assertions
    mock_Thread.assert_called()
    mock_thread.start.assert_called()
    mock_thread.join.assert_called()


def test_prototest():
    # Call the prototest function
    prototest()


if __name__ == '__main__':
    pytest.main()
