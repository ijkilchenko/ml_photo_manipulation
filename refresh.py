import os
import random
import re
import hashlib
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--path', help='Path to the images')
parser.add_argument('--rename', dest='rename', action='store_true', help='Rename all the image files')
parser.add_argument('--dry-run', dest='dry_run', action='store_true', help='Do not modify files')
parser.add_argument('--sort-by-vec', dest='sort_by_vec', action='store_true', help='Prefix new names with similarity ranking, else names are random')
parser.set_defaults(rename=False)
parser.set_defaults(dry_run=False)
parser.set_defaults(sort_by_vec=False)
args = parser.parse_args()

def md5(fname):
  hash_md5 = hashlib.md5()
  with open(os.path.join(args.path, fname), "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
      hash_md5.update(chunk)
  return hash_md5.hexdigest()


def get_random_name():
  alphabet = 'abcdefghijklmnopqrstuvwxyz'
  return ''.join([alphabet[random.randint(0, len(alphabet) - 1)] for _ in range(10)])


def main(args):
  """Get all files, drop duplicates, and randomly 
  rename the remaining files."""
  dry_run = args.dry_run
  sort_by_vec = args.sort_by_vec

  banned_exs = ['.py', '.DS_Store', '.csv', 'myenv', '.md']
  all_files = []
  for s in os.listdir(args.path):
    if not any(s.lower().endswith(t.lower()) for t in banned_exs):
      all_files.append(s)

  hashes = {}

  df = pd.read_csv(os.path.join(args.path, 'features.csv'))
  image_to_R = pd.Series(df['R'].values, index=df['images']).to_dict()

  for fname in all_files:
    if sort_by_vec:
      assert image_to_R
      try:
        this_hash = image_to_R[fname]
      except KeyError:
        #raise KeyError('Run `python featurize.py` to fix')
        pass
    else:
      this_hash = md5(fname)

    if this_hash in hashes:
      hashes[this_hash].append(fname)
    else:
      hashes[this_hash] = [fname]

  duplicates = []
  for this_hash in hashes:
    duplicates.extend(hashes[this_hash][1:])

  num_renamed = 0
  old_names = []
  new_names = []
  for fname in all_files:
    if not fname in duplicates:
      ext = re.findall('\.[^.]*', fname)[-1]
      prefix = ''
      if sort_by_vec:
        prefix = '%.4f' % image_to_R[fname]
      if args.rename:
        new_name = prefix + get_random_name() + ext
      else:
        new_name = prefix + fname
      print('Renaming %s to %s' % (fname, new_name))
      old_names.append(fname)
      new_names.append(new_name)
      num_renamed += 1
      if not dry_run:
        os.rename(os.path.join(args.path, fname), os.path.join(args.path, new_name))

  assert len(old_names) == len(new_names)
  num_chunks = 10
  old_names_list = zip(*[iter(old_names)] * (len(old_names)//num_chunks))
  new_names_list = zip(*[iter(new_names)] * (len(new_names)//num_chunks))

  for i, old_names_new_names in enumerate(zip(old_names_list, new_names_list)):
    old_names, new_names = old_names_new_names
    print('Replacing names... chunk %d out of %d' % (i+1, num_chunks))
    old_names = list(old_names)
    new_names = list(new_names)
    df.replace(old_names, list(new_names), inplace=True)

  if not dry_run:
    df.to_csv(os.path.join(args.path, 'features.csv'), index=False)

  num_deleted = 0
  for fname in duplicates:
    if sort_by_vec:
      assert image_to_R
      try:
        this_hash = image_to_R[fname]
      except KeyError:
        #raise KeyError('Run `python featurize.py` to fix')
        continue  # Do not do anything if the image is not in image_to_R (could be a gif)
    else:
      this_hash = md5(fname)
    dupes = hashes[this_hash][1:]
    print('Removing duplicate %s (similar to %s)' % (fname, dupes))
    num_deleted += 1
    if not dry_run:
      os.remove(os.path.join(args.path, fname))
 
  print()
  print('Number of files renamed: %d' % num_renamed)
  print('Number of files deleted: %d' % num_deleted)

if __name__ == '__main__':
  main(args)
