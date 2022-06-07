## M365 Chaos Script

## **Do Not Use On Production This Script Will Create and Delete Random Resources**


### Usage

#### Static Mode
```
m365_tenant_chaos.py -username [usernam] -password [password] -objectname [objectname] -banneddomain [Banned Domain]

```

#### Chaos Mode
```
m365_tenant_chaos.py -username [usernam] -password [password] -objectname [objectname] -banneddomain [Banned Domain] -maxnumber [number] -chaosmode

```
#### Setup Mode

```
m365_tenant_chaos.py -username [usernam] -password [password] -objectname [objectname] -banneddomain [Banned Domain] -setupmode

```
### Options

`-u, --username [username]`
: Enter username to use to login into M365 Tenant.

`-p, --password [password]`
: Enter password to use to login into M365 Tenant.

`-o, --objectname [objectname]`
: The default text to add to start of objects created with script.


`-b, --banneddomain [bannedomain]`
: Domain name to check and stop script it matches. Use to check for production domain.


`-m, --maxnumber [number]`
: Maximum number to use in chaos mode.


`-c, chaosmode`
: Should the script run in chaos mode.


`-s, --setupmode`
: Should the script run in setup mode.


## Remarks


## **Do Not Use On Production This Script Will Create and Delete Random Resources**


If the script runs without `-chaosmode` or `-setupmode` it eill run in static mode.  Full details on modes and what is ran under each mode be found [here](modes.md)
