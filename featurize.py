from pic2vec import ImageFeaturizer
import os

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--path', help='Path to the images')
parser.add_argument('--depth', help='Depth of Xception')
parser.set_defaults(depth=2)
args = parser.parse_args()

image_column_name = 'images'

my_featurizer = ImageFeaturizer(model='xception', depth=int(args.depth), autosample=True)

featurized_df = my_featurizer.featurize(image_column_name, image_path=args.path)

featurized_df.to_csv(os.path.join(args.path, 'features.csv'), index=False)