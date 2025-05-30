===== Create a virtual environment =====
Open Terminal, navigate to your project folder, and run: 
	python -m venv myenv

===== Activate the virtual environment =====
run:
	myenv\Scripts\activate.


===== Deactivate  the virtual environment =====
run: 
	deactivate


===== Install Required Libraries =====
run: 
	pip install requests beautifulsoup4 pandas


===== Run the Script =====
run: 
	python scrape_auctions.py


===== Make requirements.txt file =====
run: 
	pip freeze > requirements.txt


===== Install requirements.txt file =====
run: 
	pip install -r requirements.txt

============================================================================================================================================================================================================================================================

			KALI

============================================================================================================================================================================================================================================================

===== Move To Folder w/ Env =====
run: 
	cd /mnt/c/Users/heene/OneDrive/Desktop/auction_env

===== Create a virtual environment =====
run:
	└─$ python3 -m venv ~/auc_env


===== Copy README.txt and req.txt=====
To change into new env folder, run: 
	└─$ cd auc_envv 

Copy txt files, run:
	└─$ cp -r /mnt/c/Users/heene/OneDrive/Desktop/auction_env/README.txt .
	└─$ cp -r /mnt/c/Users/heene/OneDrive/Desktop/auction_env/requirements.txt .
	└─$ cp -r /mnt/c/Users/heene/OneDrive/Desktop/auction_env/scrapper.py .


===== Activate Env =====
run: 
	└─$ source ~/auc_envv/bin/activate

===== Install Required Libraries =====
run: 
	└─$ pip install -r requirements.txt

===== Deactivate  the virtual environment =====
run: 
	└─$ deactivate


===== Install Required Libraries =====
run: 
	└─$ pip install -r requirements.txt


===== Run the Script =====
run: 
	└─$ python3 auc_envv/scrape_auctions.py

===== Make requirements.txt file =====
run: 
	└─$ pip freeze > requirements.txt

=======================================================================================
To ensure outbound traffic is allowed on Kali Linux, you need to configure your firewall. 

iptables or ufw. If using iptables, you'll need to add rules to the OUTPUT chain to allow traffic. If using ufw, you'll add rules to allow traffic based on port, protocol, and source/destination. You'll also need to ensure that your network interface is configured correctly. 


===== Using iptables =====
1) Identify your network interface: Use ifconfig or ip addr to find the name of your network interface (e.g., eth0, wlan0).

2) Add rules to allow outbound traffic: 
    sudo iptables -A OUTPUT -o <interface_name> -j ACCEPT




Replace <interface_name> with the actual name of your network interface (e.g., eth0). This rule allows all traffic originating from your machine on the specified interface. 
1) Add rules to allow established and related connections: This is important for allowing responses to your outbound traffic.
Code

