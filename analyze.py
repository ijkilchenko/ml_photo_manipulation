from scipy.spatial.distance import euclidean
import pandas as pd
import numpy as np
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--path', help='Path to the images')
parser.add_argument('--fast', dest='fast', action='store_true', help='Analyze faster!')
parser.set_defaults(fast=False)
args = parser.parse_args()

df = pd.read_csv(os.path.join(args.path, 'features.csv'))
df_feat = df[[col for col in df if col.startswith('images_feat')]]
df['D'] = np.linalg.norm(df_feat, axis=1)
df = df.sort_values(by=['D']).reset_index(drop=True)

R = []
Left = df.index.tolist()
while Left:
	if len(Left) % 10 == 0:
		print('Sorting images... %d left' % len(Left))

	if not R:
		i = np.random.randint(len(Left))
		Left.remove(i)
		R.append(i)
	i = R[-1]

	best_j = Left[0]
	best_sim = np.inf

	if args.fast:
		end = 101
		limit = 1
	else:
		end = len(Left)
		limit = np.inf

	for j in Left[1:end]:
		dist = (df.iloc[i]['D'] - df.iloc[j]['D'])**2
		if dist < limit:
			sim = 1/(1 + euclidean(df_feat.iloc[i], df_feat.iloc[j]))
			if sim < best_sim:
				best_j = j
				best_sim = best_sim
		else:
			print(dist)
			break
	Left.remove(best_j)
	R.append(best_j)

df['R'] = pd.Series(R)

df = df.sort_values(by=['R']).reset_index(drop=True)

df.to_csv(os.path.join(args.path, 'features.csv'), index=False)