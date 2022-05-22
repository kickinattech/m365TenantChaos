# m365 Chaos Script

## **Do Not Use On Production This Script Will Create and Delete Random Resources**

## Purpose

This is a python script used to randomise activity in an m365 tenant. When paired with a pipeline, for example, Azure DevOps, this script allows random activity to be conducted on an M365 tenant for each night. **Do Not Use On Production This Script Will Create and Delete Random Resources**

## History

I initially created a PowerShell script for my own use in May 2021. I recreated it in a python script and updated it, and I then released it publicly on Github.

## Setup

The script needs Microsoft 365 CLI and Azure CLI to run (these can be installed as part of the pipeline if used in that way)

Before using Microsoft 365 CLI in the script, you should manually run  Microsoft 365 CLI  and login into your tenant to give it permission. Once logged in successfully, the script will be able to log in without interaction.

## Parameters 

 - -u/--username Enter username to use to login into M365 Tenant.
 - -p/--password Enter password to use to login into M365 Tenant.
 - -o/--objectname The default text to add to start of objects created with script.
 - -b/--banneddomain Domain name to check and stop script it matches.  Use to check for production domain.
 - -m/--maxnumber Maximum number to use in chaos mode.
 - -c/--chaosmode Should it run in chaos mode.
 - -s/--setupmode Should it run up in setup mode.

## ToDo

There is number of enhancments that I wish/need to do. You can see list full list of proposed enhancements [here](https://github.com/kickinattech/m365TenantChaos/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement_)
