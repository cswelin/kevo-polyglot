# kevo-polyglot
This is a Kevo Plus interface for ISY Polyglot.

MIT license.

#Requirements
`Kevo Gateway aka Kevo Plus`

Install:

1. Go to your polyglot/config/node_servers/ folder.
  * `git clone https://github.com/cswelin/kevo-polyglot`
  * `cd kevo-polyglot`
2. Add your username and password to a new file called login.py
  * `echo USERNAME='"<username>"' >> login.py`
  * `echo PASSWORD='"<password>"' >> login.py`
3. Restart Polyglot and add the Kevo nodeserver via web interface If you have the Polyglot systemctl script installed do this:
  * `sudo systemctl restart polyglot` or `sudo service polyglot restart`
4. Download the profile from the Kevo Polyglot configuration page and copy baseURL
5. Add as NodeServer in ISY. Profile Number MUST MATCH what you put in Polyglot
6. Upload profile you download from Polyglot to ISY
7. Reboot ISY
8. Upload Profile again in the node server (quirk of ISY)
9. Reboot ISY again (quirk of ISY)
10. Once ISY is back up, go to Polyglot and restart the Kevo nodeserver.
11. All Thermostats will be automatically added as 'Kevo <name>'
12. Write programs and enjoy.


einstein.42
