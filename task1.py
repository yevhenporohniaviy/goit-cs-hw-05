import asyncio
import argparse
import logging
from aiopath import AsyncPath
import aioshutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def copy_file(source_path, output_folder):
    try:
        extension = source_path.suffix[1:].lower()
        output_dir = AsyncPath(output_folder) / extension
        await output_dir.mkdir(parents=True, exist_ok=True)
        
        await aioshutil.copy(source_path, output_dir / source_path.name)
        logging.info(f"File {source_path} copied to {output_dir / source_path.name}")
    except Exception as e:
        logging.error(f"Error copying file {source_path}: {e}")

async def read_folder(source_folder, output_folder):
    source_path = AsyncPath(source_folder)
    tasks = []
    
    async for file_path in source_path.glob('**/*'):
        if await file_path.is_file():
            tasks.append(copy_file(file_path, output_folder))
    
    await asyncio.gather(*tasks)

async def main():
    parser = argparse.ArgumentParser(description="Sort files by extension")
    parser.add_argument("source_folder", help="Source folder path")
    parser.add_argument("output_folder", help="Output folder path")
    args = parser.parse_args()

    await read_folder(args.source_folder, args.output_folder)

if __name__ == "__main__":
    asyncio.run(main())