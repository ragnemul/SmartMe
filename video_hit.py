import sys
import argparse
from tqdm import tqdm
import os
import json
import cv2
import numpy as np



class KeyFrames (object):

    def __init__(self, json_hash, kf_dir, method, dist):
        [self.json_hash, self.keyframes_path, self.method, self.dist] = [json_hash, kf_dir, method, dist]

        if not os.path.isdir(self.keyframes_path):
            print("Cannot open key frames directory", self.keyframes_path)
            exit()

        if self.method == "average":
            self.hash = cv2.img_hash.AverageHash_create()
        if self.method == "phash":
            self.hash = cv2.img_hash.PHash_create()
        if self.method == "color":
            self.hash = cv2.img_hash.ColorMomentHash_create()

        print ("json_hash: ", json_hash)
        print ("Key frames directory: ", kf_dir)

        self.key_filename = os.path.basename(self.json_hash)
        self.key = os.path.splitext(self.key_filename)[0]
        with open(self.json_hash) as json_file:
            file_data = json.load(json_file)
        self.frame_hash = file_data[self.key][0]['hash']


    def __del__(self):
        print("Freeing resources")
        print("Terminate")

    @staticmethod
    def hamming(a, b):
        return bin(int(a) ^ int(b)).count('1')

    def distance(self, hash1, hash2):
        return self.hash.compare(hash1, hash2)

    def locate(self):
        video_file = None

        for root, dirs, files in os.walk(self.keyframes_path):
            for file in files:
                if not file.endswith('.json'):
                    continue
                with open(self.keyframes_path + "/" + file) as json_file:
                    data = json.load(json_file)

                key = os.path.splitext(file)[0]
                hits = [self.distance(np.asarray(data[key][i]['hash']), np.asarray(self.frame_hash)) <= self.dist for i in range(len(data[key]))]
                if sum(hits) >= 1:
                    print (self.keyframes_path + "/" + file, " video hit!")
        return video_file


def check_args(args=None):
    parser = argparse.ArgumentParser(description='Video process')
    parser.add_argument("--json_hash", help="json that contains hash", required=True)
    parser.add_argument("--keyframes_path", help="path of key frames", required=True)
    parser.add_argument('--distance', type=int, help='image distance', default=0)
    parser.add_argument('--method', help='hash method', default='average', choices=['average', 'phash', 'color'])

    results = parser.parse_args(args)

    return results.json_hash, results.keyframes_path, results.method, results.distance


def main(json_hash, kf_path, hash_method, hash_dist):
    keyframe = KeyFrames(json_hash, kf_path, hash_method, hash_dist)
    keyframe.locate()
    return 0


if __name__ == '__main__':
    json_hash, keyframes_path, method, distance = check_args(sys.argv[1:])
    sys.exit(main(json_hash, keyframes_path, method, distance))

