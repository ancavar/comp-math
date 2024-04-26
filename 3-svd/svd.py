import argparse
import numpy as np
from PIL import Image
from power_svd import power_method
from jacobi_svd import jacobi_method
import struct

# SVD Compressed Unified Format
SCUF_FORMAT = "<4s32sIIII" 

def save_scuf(file_path, image_type, image_size, ratio, payload):
    with open(f'{file_path}.scf', "wb") as file:
        file.write(struct.pack(SCUF_FORMAT, b'SCUF', image_type.encode("utf-8"), *image_size, ratio))
        file.write(payload)

def load_scuf(file_path):
    with open(file_path, "rb") as file:
        signature, image_type, width, height, channels, k = struct.unpack(SCUF_FORMAT, file.read(struct.calcsize(SCUF_FORMAT)))
        payload = file.read()

    return signature.decode("utf-8"), image_type.decode("utf-8"), (width, height, channels), k, payload

def compress_image(in_file, out_file, ratio, svd):
    with Image.open(in_file) as image:
        image_data = np.array(image)

    m, n = image.size
    k = int(n * m / (4 * ratio * (n + m + 1)))
    payload = b""
    for channel in range(3):
        channel_data = image_data[:, :, channel]
        U, s, VT = svd(channel_data)
        payload += U[:, :k].tobytes() + s[:k].tobytes() + VT[:k, :].tobytes()

    save_scuf(out_file, "BMP", image_data.shape, k,  payload)

def decompress_image(in_file, out_file):
    signature, image_type, image_size, k, payload = load_scuf(in_file)
    if signature != 'SCUF':
        raise ValueError(f'Incorrect file format: SCUF expected, ${signature} received')
    # elif image_type != 'BMP':
    #     raise ValueError('Incorrect image format: only BMP is supported')

    width, height, channels = image_size
    compressed_data = {}
    offset, count = 0, 0
    for channel in range(3):
        # horrible
        offset, count = offset + count * 8, width*k
        compressed_data[f'U{channel}'] = np.frombuffer(payload, dtype=np.float64, count = count, offset=offset).reshape((width, k))
        offset, count = offset + count * 8, k
        compressed_data[f's{channel}'] = np.frombuffer(payload, dtype=np.float64, count = count, offset = offset)
        offset, count = offset + count * 8, height * k 
        compressed_data[f'V{channel}'] = np.frombuffer(payload, dtype=np.float64, count = count, offset=offset).reshape((k, height))

    reconstructed_image = np.zeros((width, height, channels), dtype=np.uint8)
    for channel in range(3):
        U, s, VT = compressed_data[f'U{channel}'], compressed_data[f's{channel}'], compressed_data[f'V{channel}']
        reconstructed_image[:, :, channel] = (U @ np.diag(s) @ VT).clip(0, 255).astype(np.uint8)
    image = Image.fromarray(reconstructed_image.astype(np.uint8))
    image.save(out_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute SVD of a BMP image')
    subparsers = parser.add_subparsers(dest='mode')

    compress_parser = subparsers.add_parser('compress')
    compress_parser.add_argument('--method', type=str, choices=['numpy', 'simple', 'advanced'], required=True)
    compress_parser.add_argument('--compression', type=int, required=True)
    compress_parser.add_argument('--in_file', type=str, required=True)
    compress_parser.add_argument('--out_file', type=str, required=True)

    decompress_parser = subparsers.add_parser('decompress')
    decompress_parser.add_argument('--in_file', type=str, required=True)
    decompress_parser.add_argument('--out_file', type=str, required=True)

    args = parser.parse_args()

    methods = {
        'numpy': np.linalg.svd,
        'simple': power_method,
        'advanced': jacobi_method
    }

    if args.mode == 'compress':
        compress_image(args.in_file, args.out_file, args.compression, methods[args.method])
    elif args.mode == 'decompress':
        decompress_image(args.in_file, args.out_file)