from pyseg2.rawseg2 import read_raw_seg2
from HDF5DataModel.Model.subclasses import AcqSig
from datetime import datetime


def read_seg2_file(filepath: str) -> AcqSig:
    """
    Read a SEG2 file and return an AcqSig object containing the data and metadata.
    The function uses the pyseg2 library to read the SEG2 file and extracts relevant
    metadata to populate the attributes of the AcqSig and its traces.

    Parameters:
    filepath (str): Path to the SEG2 file.

    Returns:
    AcqSig: An AcqSig object containing the traces and their metadata.
    """
    fileheader, trace_header_and_data = read_raw_seg2(filepath, evaluate_types=True)
    sig = AcqSig()
    sig.attrs.set_attrs_from_dict(fileheader)

    sig.attrs.start_time = datetime.strptime(sig.attrs.ACQUISITION_DATE + sig.attrs.ACQUISITION_TIME, '%d/%m/%Y%H:%M:%S').timestamp()
    del sig.attrs.ACQUISITION_DATE
    del sig.attrs.ACQUISITION_TIME
    sig.attrs.traces_number = len(trace_header_and_data)

    for trace_index, (trace_header, trace_data) in enumerate(trace_header_and_data):
        trace = sig.add_trace(name=f"Trace[{trace_index}]")
        trace.data = trace_data.astype('float32')
        trace.attrs.set_attrs_from_dict(trace_header)
        trace.attrs.index = trace_index
        del trace.attrs.CHANNEL_NUMBER
        trace.attrs.sampling_freq = 1 / float(trace.attrs.SAMPLE_INTERVAL)
        del trace.attrs.SAMPLE_INTERVAL
        trace.attrs.pretrig_duration = float(trace.attrs.DELAY)
        del trace.attrs.DELAY
        position = [float(x) for x in trace.attrs.RECEIVER_LOCATION.split()]
        trace.attrs.position_x = position[0]
        trace.attrs.position_y = position[1] if len(position) > 1 else 0.0
        trace.attrs.position_z = position[2] if len(position) > 2 else 0.0
        del trace.attrs.RECEIVER_LOCATION
    return sig


if __name__ == '__main__':
    sig = read_seg2_file(r'C:\Users\devie\Documents\Programmes\ABCScanViewers\abcscanviewers\bscanviewer\seg2file_musc.sg2')
