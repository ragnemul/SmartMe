import sys
import argparse
from tqdm import tqdm
import os
import json
import cv2



class KeyFrames (object):

    def __init__(self, hash, kf_dir, method, dist):
        [self.frame_hash, self.keyframes_path, self.method, self.dist] = [hash, kf_dir, method, dist]

        if not os.path.isdir(self.keyframes_path):
            print("Cannot open key frames directory", self.keyframes_path)
            exit()

        if method == "average":
            self.hash = cv2.img_hash.AverageHash_create()

        print ("hash: ", hash)
        print ("Key frames directory: ", kf_dir)

    def __del__(self):
        print("Freeing resources")
        print("Terminate")

    @staticmethod
    def hamming(a, b):
        return bin(int(a) ^ int(b)).count('1')

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
                if not file.endswith('.json'):
                    continue
                with open(self.keyframes_path + "/" + file) as json_file:
                    data = json.load(json_file)

                key = os.path.splitext(file)[0]
                hits = [self.distance(data[key][i]['hash'], self.frame_hash) <= self.dist for i in range(len(data[key]))]
                if sum(hits) >= 1:
                    print (self.keyframes_path + "/" + file, " video hit!")
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
    keyframe.locate()
    return 0


if __name__ == '__main__':
    hash, keyframes_path, method, distance = check_args(sys.argv[1:])
    sys.exit(main(hash, keyframes_path, method, distance))

