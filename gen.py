import hashlib
import string
import os
from time import time

def batch_generator(charset, length, batch_size):
    """高效生成批量密码组合（纯字节操作）"""
    chars = tuple(charset)
    char_len = len(charset)
    total = char_len ** length
    
    # 预计算字符的字节表示
    char_bytes = [c.encode('utf-8') for c in chars]
    
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch = bytearray()
        
        for i in range(start, end):
            indices = []
            val = i
            for _ in range(length):
                indices.append(val % char_len)
                val = val // char_len
            
            # 直接构建字节数组，避免字符串操作
            password_bytes = b''.join(char_bytes[idx] for idx in reversed(indices))
            batch.extend(password_bytes)
            batch.extend(b' ')
            batch.extend(hashlib.sha256(password_bytes).digest().hex().encode('ascii'))
            batch.extend(b'\n')
        
        yield bytes(batch)

def optimized_generate_hashes(length, charset=string.digits + string.ascii_letters, batch_size=1000000):
    """高效生成密码及其哈希值（纯字节流）"""
    total = len(charset) ** length
    batches = (total + batch_size - 1) // batch_size
    
    for i, data_batch in enumerate(batch_generator(charset, length, batch_size)):
        yield data_batch
        if i % 10 == 0:
            progress = min((i * batch_size) / total * 100, 100)
            print(f"\r进度: {progress:.2f}%", end='')
    print("\r进度: 100.00%")

def process_length(length, charset, batch_size, output_file):
    """处理单个长度并直接写入文件"""
    start_time = time()
    print(f"\n处理长度为{length}的密码组合...")
    
    with open(output_file, "ab") as file:  # 追加模式
        for batch in optimized_generate_hashes(length, charset, batch_size):
            file.write(batch)
    
    elapsed = time() - start_time
    print(f"长度{length}处理完成，耗时: {elapsed:.2f}秒")
    return elapsed

if __name__ == "__main__":
    start_time = time()
    output_file = "sha256.txt"
    
    # 确保文件不存在或为空
    if os.path.exists(output_file):
        os.remove(output_file)
    with open("length.txt", "r") as f:
        lines = f.readlines()
        length = int(lines[0].strip())
    charset = string.digits + string.ascii_letters
    batch_size = 1000000  # 根据内存调整
    
    process_length(length, charset, batch_size, output_file)
    
    total_time = time() - start_time
    print(f"\n全部完成！总耗时: {total_time:.2f}秒")
    print(f"文件大小: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
