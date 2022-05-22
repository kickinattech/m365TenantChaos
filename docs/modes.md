# Modes

## **Do Not Use On Production This Script Will Create and Delete Random Resources**

## Types

The script has three modes.

| Mode | Info |
|:-----:|:-----:|
| Static | If setup or chaos is not set the script will run in static mode and create/delete three of each resource |
| Setup | Will create 100 of each resource type |
| Chaos| Will run in chaos mode and each create/delete of resource type will choose random number between 0 and number set with in maxnumber parameters|

## Jobs Run Under Each Mode Type

| Mode | Info |
|:-----:|:-----:|
| Static | New Teams, New Apps, New Groups, Add Channels, Remove Teams, Remove Apps, Remove Groups|
| Setup | New Teams, New Apps, New Groups, Add Channels |
| Chaos|  New Teams, New Apps, New Groups, Add Channels, Remove Teams, Remove Apps, Remove Groups|

##Job Types

All removes gets objects starting with string set in the objectname argument.

| Job Type | Info |
|:-----:|:-----:|
| New Teams |Adds Random Teams|
| New Apps |Adds Randopm App Registration |
| New Groups|Adds random groups|
| Add Channels|Adds random channels to random teams groups|
| Remove Teams|Removes random teams|
| Remove App|Removes random app registration|
| Remove Groups|Removes random groups|


