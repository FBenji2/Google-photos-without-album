# Google-photos-without-album
Python program that lists all URLs of google photos which are not in any album or archived and are not shared.
I know that this might be something that not so technical people also want, so I will try to make it simple with steps and images:

How to use (as of 14/07/2024):
1. Go to https://console.cloud.google.com/ and login with your google account
2. Create a new project:
  ![image](https://github.com/user-attachments/assets/46954db9-b50a-4b5e-9629-3c28a1c39e9b)
  ![image](https://github.com/user-attachments/assets/0f60082f-28d6-408e-8215-64fa217addad)
3. Give it a name and click "create"
  ![image](https://github.com/user-attachments/assets/ccf0e180-9503-4c6e-918a-d976182168ad)
4. It will take a few seconds to have the new project created, so be patient.
5. When it't done, switch to the new project:
  ![image](https://github.com/user-attachments/assets/46954db9-b50a-4b5e-9629-3c28a1c39e9b)
  ![image](https://github.com/user-attachments/assets/d4ec8ee2-e995-4c88-a017-9d7609ae7a7d)
6. Go to "APIs and services" and look for "library" on the left:
  ![image](https://github.com/user-attachments/assets/238647ed-cdd2-47fc-a3ac-a0f551080e08)
  ![image](https://github.com/user-attachments/assets/e38d8134-50bc-4626-bfe5-06380f1550e2)
7. In the API library search for "google photos api":
  ![image](https://github.com/user-attachments/assets/6f70780f-dcb3-495a-bbe3-fd5c5dab796f)
8. When the results show up, select the "Photos library API" and enable it:
  ![image](https://github.com/user-attachments/assets/9c4c809e-f387-4d3f-a0d4-9f5105ce4ffd)
  ![image](https://github.com/user-attachments/assets/d228c632-b128-4cb8-9380-14945f3f24f5)
9. On the left go to "credentials", then "create credentials" at the top and select "OAuth client ID":
  ![image](https://github.com/user-attachments/assets/b9e31cf2-1031-4fad-910f-0ac46a6b023a)
  ![image](https://github.com/user-attachments/assets/31a75605-93a6-4f82-a113-c86771633a8e)
10. On the right, click "configure consent screen". If this button doesn't exist but there is a dropdown menu where the application type can be selected, go to step 16:
  ![image](https://github.com/user-attachments/assets/7e3c978d-19dd-4a03-b6cc-1f24c79ad993)
11. Set up the consent as such:
  ![image](https://github.com/user-attachments/assets/9b287222-6571-40fe-bf7d-a1fc3f154ace)
  ![image](https://github.com/user-attachments/assets/97ccf6ab-744d-4650-be4e-bb00ec2bba45)
12. In the "scopes" section, add the google photos related scopes. In reality only "https://www.googleapis.com/auth/photoslibrary" and "https://www.googleapis.com/auth/photoslibrary.sharing" is enough for the script I uploaded but if you want to play around with the code, you should add all.
  ![image](https://github.com/user-attachments/assets/084b448a-5a3b-4d2d-bb32-826b11cb69d9)
13. After adding them, it should look like this (if all were added), click "save and continue" to proceed:
  ![image](https://github.com/user-attachments/assets/0a042352-4ae3-4795-8a2d-872eb50c8fd7)
14. On the "Test users" page, add your own email as a test user, if you can't do that, then just skip it, pretty sure it added it for me automatically:
  ![image](https://github.com/user-attachments/assets/096aa760-36b2-496c-ab01-4934c509eabc)
15. A summary will show at the next step, make sure that everything is correct:
  ![image](https://github.com/user-attachments/assets/4d4c9ae7-04b8-4d01-8d2d-778557438302)
16. Repeat step 9, but this time instead of the "configure consent screen" option a dropdown will show up, where select "Desktop app" and give it a name and then create it:
  ![image](https://github.com/user-attachments/assets/779b5961-4336-4ba0-97f9-13a8df579fab)
17. After it's created, a window will show up where you can download the JSON file which is necessary for authentication:
    ![image](https://github.com/user-attachments/assets/396e0bff-8b4b-48a5-b36c-73b0b48f7f72)
18. Clone/download the contents of this repository into a folder.
19. Place the downloaded JSON file in the same folder as the "pwa.py" file you just downloaded/cloned and name it "OAuth Client.json", or make sure that the "client_secret_file" variable in "pwa.py" is set to the same value as this json's name.
20. Install python, there are countless tutorials for it, you can get it from their website: https://www.python.org/downloads/
21. Install pip for python, check a tutorial on how to do it
22. Install "google-auth-oauthlib" and "google-api-python-client" with pip by running "pip install google-auth-oauthlib google-api-python-client". (you might need to put "--user" like so: "pip install --user google-auth-oauthlib google-api-python-client" if it doesn't work, I had an issue with it)
23. With command line go to where the "pwa.py" is and execute it with python (look up a tutorial for this if this is not familiar to you)
24. When running the app for the first time, google will promt you to log in, allow all things requested and log in.
25. After it executes, it creates a file called "Images not in albums.txt", where each line contains a photo's link that is not in any album and is also not archived, but was uploaded/saved by you.
26. Use that information for whatever you want to, also feel free to play around with the code to tailor it for your needs.

Feel free to provide feedback at fbenji2@gmail.com
