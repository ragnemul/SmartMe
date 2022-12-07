import sys
import argparse
from tqdm import tqdm
import os
import json



class KeyFrames (object):

    def __init__(self, hash, kf_dir, method, dist):
        [self.hash, self.keyframes_path, self.method, self.dist] = [hash, kf_dir, method, dist]

        if not os.path.isdir(self.keyframes_path):
            print("Cannot open key frames directory", self.keyframes_path)
            exit()

        print ("hash: ", hash)
        print ("Key frames directory: ", kf_dir)

    def __del__(self):
        print("Freeing resources")
        print("Terminate")

    def distance(self, hash1, hash2):
        if self.method == "phash" or self.method == "dhash":
            return self.hamming(hash1, hash2)
        elif self.method == "average":
            return self.hash.compare(hash1, hash2)
        else:
            float("inf")

    def locate(self):
        video_file = None

        for root, dirs, files in os.walk(self.keyframes_path):
            for file in files:

                f = open(self.keyframes_path+"/"+file)
                data = json.load(f)
                if self.distance(data['hash'], self.hash) <= self.dist:
                    pass
        return video_file


def check_args(args=None):
    parser = argparse.ArgumentParser(description='Video process')
    parser.add_argument("--hash", help="video source", required=True)
    parser.add_argument("--keyframes_path", help="path of key frames", required=True)
    parser.add_argument('--distance', type=int, help='image distance', default=0)
    parser.add_argument('--method', help='hash method', default='average', choices=['average', 'phash', 'dhash'])

    results = parser.parse_args(args)

    return results.hash, results.keyframes_path, results.method, results.distance


def main(hash_key, kf_path, hash_method, hash_dist):
    keyframe = KeyFrames(hash_key, kf_path, hash_method, hash_dist)
    video_hit = keyframe.locate()
    if video_hit != None:
        print ("Video hit: ", video_hit)


if __name__ == '__main__':
    hash, keyframes_path, method, distance = check_args(sys.argv[1:])
    sys.exit(main(hash, keyframes_path, method, distance))

