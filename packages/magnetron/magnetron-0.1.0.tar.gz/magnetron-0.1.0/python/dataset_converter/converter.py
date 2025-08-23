# (c) 2025 Mario "Neo" Sieg. <mario.sieg.64@gmail.com>

# This script converts datasets from industry adapted formats like pickle, safetensors, onnx etc. to the Magnetron data format.

import magnetron as mag
from magnetron.io import StorageStream
from pathlib import Path
import pickle


def convert_pickle(input_file_path: Path | str, output_file_path: Path | str | None) -> None:
    if isinstance(input_file_path, str):
        input_file_path = Path(input_file_path)
    if isinstance(output_file_path, str):
        output_file_path = Path(output_file_path)
    assert output_file_path.suffix == '.mag', 'Output file must have .mag extension'
    with open(input_file_path, 'rb') as f:
        data = pickle.load(f)
    if output_file_path is None:
        output_file_path = input_file_path.with_suffix('.mag')
    output = StorageStream()
    for key in data:
        if key.endswith('w'):
            output.put(key, mag.Tensor.from_data(data[key], name=key).T)  # Transpose weights
        else:
            output.put(key, mag.Tensor.from_data(data[key], name=key))
    output.serialize(output_file_path)


INPUT = Path('../examples/interactive/mnist_interactive/mnist_mlp_weights.pkl')
OUTPUT = Path('out.mag')
convert_pickle(INPUT, OUTPUT)

inp = StorageStream.open(OUTPUT)
print(inp.get('fc1_w'))
print(inp.get('fc1_b'))
print(inp.get('fc2_w'))
print(inp.get('fc2_b'))
