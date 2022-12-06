import sys
import argparse
import cv2
from tqdm import tqdm
import os
import json



class Video (object):

    def __init__(self, src, dst, dist, meth, crop):
        [self.video_source, self.destination_path, self.dist, self.method, self.cropping] = \
            [src, dst, dist, meth, crop]

        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened():
            print("Cannot open video source", self.video_source)
            exit()

        self.length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.frames = []
        self.key_frames = []
        self.cropping_val = round(self.cropping / 100,2)

        if meth == "average":
            self.hash = self.hash = cv2.img_hash.AverageHash_create()

        print ("Video source: ", src)
        print ("Destination path: ", dst)
        print ("Method:", meth)
        print ("Distance: ", dist)
        print ("Cropping %: ", self.cropping)

    def __del__(self):
        print("Freeing resources")

        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()

        print("Terminate")


    @staticmethod
    def dhash(cv_image, hash_size=8):
        resized = cv2.resize(cv_image, (hash_size + 1, hash_size))
        diff = resized[:, 1:] > resized[:, :-1]
        return sum([2 ** i for i, v in enumerate(diff.flatten()) if v])

    @staticmethod
    def pHash(cv_image):
        img = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        h = cv2.img_hash.pHash(img)  # 8-byte hash
        ph = int.from_bytes(h.tobytes(), byteorder='big', signed=False)
        return ph

    @staticmethod
    def hamming(a, b):
        """
        Calcula la distancia Hamming entre a y b.
        """
        return bin(int(a) ^ int(b)).count('1')


    def distance(self, hash1, hash2):
        if self.method == "phash" or self.method == "dhash":
            return self.hamming(hash1, hash2)
        elif self.method == "average":
            return self.hash.compare(hash1, hash2)
        else:
            float("inf")


    def load_video(self):
        for _ in tqdm(range(self.length), desc="Loading video"):
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = frame[int(self.height * self.cropping_val):int(self.height - self.height * self.cropping_val),0:self.width]

            if self.method == "phash":
                hash_val = self.pHash(frame)
            elif self.method == "dhash":
                hash_val = self.dhash(frame)
            else:
                hash_val = self.hash.compute(frame)

            frame_dict = {
                "frame": frame,
                "hash": hash_val
            }
            self.frames.append(frame_dict)

    def get_key_frames(self):
        return self.key_frames

    def get_frames(self):
        return self.frames

    @staticmethod
    def show_video(frames):
        for frame in tqdm(list(frames), desc="Showing video"):
            cv2.imshow("Video", frame['frame'])  # show frame
            if cv2.waitKey(1) & 0xFF == ord('q'):  # on press of q break
                break

    def process_video(self):
        i = 0
        pbar = tqdm(total = self.length, desc="Processing video")
        while i < self.length:
            first = self.frames[i]
            #cv2.imshow("first", first["frame"])
            i += 1
            incr = 1
            for j in range(i, self.length):
                second = self.frames[j]
                if  self.distance(first['hash'], second['hash']) >= self.dist:
                    #print ("Almacenando frame ",i-1)
                    #cv2.imshow("almacenado", second["frame"])
                    self.key_frames.append(first)
                    incr = j-i+1
                    i=j
                    #cv2.waitKey()
                    break

            if cv2.waitKey(1) & 0xFF == ord('q'):  # on press of q break
                break
            pbar.update(incr)

        pbar.close()


    def save_key_frames(self):
        for key_frame in tqdm(list(self.key_frames), desc="Writing files"):
            name = self.destination_path + '/' + str(key_frame['hash']) + '.jpg'
            cv2.imwrite(name, key_frame['frame'])

# Hacer JSON especiifcando nombre de fichero con los campos: hash, method, distance

    def write_key_frames_hashes(self):
        file_name = os.path.basename(self.video_source)
        data = {}
        data.setdefault(name)

        for key_frame in tqdm(list(self.key_frames), desc="Writing files"):



            f = open(name, "a")
            json_str = json.dumps([os.path.basename(self.video_source), {'hash_method': (self.method)}, {'distance': (self.dist)}, {'cropping':(self.cropping)}])
            f.write(json_str)
            f.close()


    def check_hits(self):
        hits = 0
        for frame in tqdm(list(self.frames), desc="Checking hits"):
            for key_frame in (list(self.key_frames)):
                if self.distance(frame['hash'], key_frame['hash']) <= self.dist:
                    hits += 1
                    break
        print ("Hits: ", hits, "/", self.length)




def check_args(args=None):
    parser = argparse.ArgumentParser(description='Video process')
    parser.add_argument("--source", help="video source", required=True)
    parser.add_argument("--destination_path", help="path for storing the frames", required=True)
    parser.add_argument('--distance', type=int, help='image distance', default=0)
    parser.add_argument('--method', help='hash method', default='average', choices=['average', 'phash', 'dhash'])
    parser.add_argument('--cropping', type=int, help='vertical cropping percentaje over the image (do not type percentaje sign here) ', default=33)

    results = parser.parse_args(args)
    if not (results.cropping >= 0 and results.cropping < 50):
        results.cropping = 33

    return results.source, results.destination_path, results.distance, results.method, results.cropping


def main(src, dst, dist, meth, crop):
    video = Video(src, dst, dist, meth, crop)
    video.load_video()

    video.process_video()
    video.check_hits()
    video.write_key_frames_hashes()

    video.show_video(video.get_key_frames())
    #cv2.waitKey()



if __name__ == '__main__':
    source, destination, distance, method, crop = check_args(sys.argv[1:])
    sys.exit(main(source, destination, distance, method, crop))

