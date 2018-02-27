# **craft ai** API python client #

[![PyPI](https://img.shields.io/pypi/v/craft-ai.svg?style=flat-square)](https://pypi.python.org/pypi?:action=display&name=craft-ai) [![Build Status](https://img.shields.io/travis/craft-ai/craft-ai-client-python/master.svg?style=flat-square)](https://travis-ci.org/craft-ai/craft-ai-client-python) [![License](https://img.shields.io/badge/license-BSD--3--Clause-42358A.svg?style=flat-square)](LICENSE) [![python](https://img.shields.io/pypi/pyversions/craft-ai.svg?style=flat-square)](https://pypi.python.org/pypi?:action=display&name=craft-ai)

[**craft ai** _AI-as-a-service_](http://craft.ai) enables your services to learn every day: provide a personalized experience to each user and automate complex tasks.

## Get Started! ##

### 0 - Signup ###

If you're reading this you are probably already registered with **craft ai**, if not, head to [`https://beta.craft.ai/signup`](https://beta.craft.ai/signup).

### 1 - Create a project ###

Once your account is setup, let's create your first **project**! Go in the 'Projects' tab in the **craft ai** control center at [`https://beta.craft.ai/projects`](https://beta.craft.ai/projects), and press **Create a project**.

Once it's done, you can click on your newly created project to retrieve its tokens. There are two types of tokens: **read** and **write**. You'll need the **write** token to create, update and delete your agent.

### 2 - Setup ###

#### Install ####

#### [PIP](https://pypi.python.org/pypi/pip/) / [PyPI](https://pypi.python.org/pypi) ####

Let's first install the package from pip.

```sh
pip install --upgrade craft-ai
```
Then import it in your code

```python
import craftai
```
> This client also provides helpers to use it in conjuction with [pandas](#pandas-support)

#### Initialize ####

```python
config = {
    "token": "{token}"
}
client = craftai.Client(config)
```

### 3 - Create an agent ###

**craft ai** is based on the concept of **agents**. In most use cases, one agent is created per user or per device.

An agent is an independent module that stores the history of the **context** of its user or device's context, and learns which **decision** to take based on the evolution of this context in the form of a **decision tree**.

In this example, we will create an agent that learns the **decision model** of a light bulb based on the time of the day and the number of people in the room. In practice, it means the agent's context have 4 properties:

- `peopleCount` which is a `continuous` property,
- `timeOfDay` which is a `time_of_day` property,
- `timezone`, a property of type `timezone` needed to generate proper values for `timeOfDay` (cf. the [context properties type section](#context-properties-types) for further information),
- and finally `lightbulbState` which is an `enum` property that is also the output.

```python
agent_id = "my_first_agent"
configuration = {
    "context": {
        "peopleCount": {
            "type": "continuous"
        },
        "timeOfDay": {
            "type": "time_of_day"
        },
        "timezone": {
            "type": "timezone"
        },
        "lightbulbState": {
            "type": "enum"
        }
    },
    "output": ["lightbulbState"]
}

agent = client.create_agent(configuration, agent_id)
print("Agent", agent["id"], "has successfully been created")
```

Pretty straightforward to test! Open [`https://beta.craft.ai/inspector`](https://beta.craft.ai/inspector), select you project and your agent is now listed.

Now, if you run that a second time, you'll get an error: the agent `'my_first_agent'` is already existing. Let's see how we can delete it before recreating it.

```python
agent_id = "my_first_agent"
client.delete_agent(agent_id)
print("Agent", agent_id, "no longer exists")

configuration = ...
agent = client.create_agent(configuration, agent_id)
print("Agent", agent["id"], "has successfully been created")
```

_For further information, check the ['create agent' reference documentation](#create)._

### 4 - Add context operations ###

We have now created our first agent but it is not able to do much, yet. To learn a decision model it needs to be provided with data, in **craft ai** these are called context operations.

In the following we add 8 operations:

1. The initial one sets the initial state of the agent, on July 25 2016 at 5:30, in Paris, nobody is there and the light is off;
2. At 7:02, someone enters the room the light is turned on;
3. At 7:15, someone else enters the room;
4. At 7:31, the light is turned off;
5. At 8:12, everyone leaves the room;
6. At 19:23, 2 persons enter the room;
7. At 22:35, the light is turned on;
8. At 23:06, everyone leaves the room and the light is turned off.

```python
agent_id = "my_first_agent"
client.delete_agent(agent_id)
print("Agent", agent_id, "no longer exists")

configuration = ...
agent = client.create_agent(configuration, agent_id)
print("Agent", agent["id"], "has successfully been created")

context_list = [
    {
        "timestamp": 1469410200,
        "context": {
            "timezone": "+02:00",
            "peopleCount": 0,
            "lightbulbState": "OFF"
        }
    },
    {
        "timestamp": 1469415720,
        "context": {
            "peopleCount": 1,
            "lightbulbState": "ON"
        }
    },
    {
        "timestamp": 1469416500,
        "context": {
            "peopleCount": 2
        }
    },
    {
        "timestamp": 1469417460,
        "context": {
            "lightbulbState": "OFF"
        }
    },
    {
        "timestamp": 1469419920,
        "context": {
            "peopleCount": 0
        }
    },
    {
        "timestamp": 1469460180,
        "context": {
            "peopleCount": 2
        }
    },
    {
        "timestamp": 1469471700,
        "context": {
            "lightbulbState": "ON"
        }
    },
    {
        "timestamp": 1469473560,
        "context": {
            "peopleCount": 0,
            "lightbulbState": "OFF"
        }
    }
]
client.add_operations(agent_id, context_list)
print("Successfully added initial operations to agent", agent_id, "!")
```

In real-world applications, you'll probably do the same kind of things when the agent is created and then, regularly throughout the lifetime of the agent with newer data.

_For further information, check the ['add context operations' reference documentation](#add-operations)._

### 5 - Compute the decision tree ###

The agent has acquired a context history, we can now compute a decision tree from it! A decision tree models the output, allowing us to estimate what the output would be in a given context.

The decision tree is computed at a given timestamp, which means it will consider the context history from the creation of this agent up to this moment. Let's first try to compute the decision tree at midnight on July 26, 2016.

```python
agent_id = "my_first_agent"

client.delete_agent(agent_id)
print("Agent", agent_id, "no longer exists")

configuration = ...
agent = client.create_agent(configuration, agent_id)
print("Agent", agent["id"], "has successfully been created")

context_list = ...
client.add_operations(agent_id, context_list)
print("Successfully added initial operations to agent", agent_id, "!")

dt_timestamp = 1469476800
decision_tree = client.get_decision_tree(agent_id, dt_timestamp)
print("The full decision tree at timestamp", dt_timestamp, "is the following:")
print(decision_tree)
""" Outputed tree is the following
  {
    '_version':'1.1.0',
    'trees':{
      'lightbulbState':{
        'children':[
          {
            'children':[
              {
                'confidence':0.6774609088897705,
                'decision_rule':{
                  'operand':0.5,
                  'operator':'<',
                  'property':'peopleCount'
                },
                'predicted_value':'OFF'
              },
              {
                'confidence':0.8630361557006836,
                'decision_rule':{
                  'operand':0.5,
                  'operator':'>=',
                  'property':'peopleCount'
                },
                'predicted_value':'ON'
              }
            ],
            'decision_rule':{
              'operand':[
                5,
                5.6666665
              ],
              'operator':'[in[',
              'property':'timeOfDay'
            }
          },
          {
            'children':[
              {
                'confidence':0.9947378635406494,
                'decision_rule':{
                  'operand':[
                    5.6666665,
                    20.666666
                  ],
                  'operator':'[in[',
                  'property':'timeOfDay'
                },
                'predicted_value':'OFF'
              },
              {
                'children':[
                  {
                    'confidence':0.969236433506012,
                    'decision_rule':{
                      'operand':1,
                      'operator':'<',
                      'property':'peopleCount'
                    },
                    'predicted_value':'OFF'
                  },
                  {
                    'confidence':0.8630361557006836,
                    'decision_rule':{
                      'operand':1,
                      'operator':'>=',
                      'property':'peopleCount'
                    },
                    'predicted_value':'ON'
                  }
                ],
                'decision_rule':{
                  'operand':[
                    20.666666,
                    5
                  ],
                  'operator':'[in[',
                  'property':'timeOfDay'
                }
              }
            ],
            'decision_rule':{
              'operand':[
                5.6666665,
                5
              ],
              'operator':'[in[',
              'property':'timeOfDay'
            }
          }
        ]
      }
    },
    'configuration':{
      'time_quantum':600,
      'learning_period':9000000,
      'context':{
        'peopleCount':{
          'type':'continuous'
        },
        'timeOfDay':{
          'type':'time_of_day',
          'is_generated':True
        },
        'timezone':{
          'type':'timezone'
        },
        'lightbulbState':{
          'type':'enum'
        }
      },
      'output':[
        'lightbulbState'
      ]
    }
  }
"""
```

Try to retrieve the tree at different timestamps to see how it gradually learns from the new operations. To visualize the trees, use the [inspector](https://beta.craft.ai/inspector)!

_For further information, check the ['compute decision tree' reference documentation](#compute)._

### 6 - Take a decision ###

Once the decision tree is computed it can be used to take a decision. In our case it is basically answering this type of question: "What is the anticipated **state of the lightbulb** at 7:15 if there are 2 persons in the room ?".

```python
agent_id = "my_first_agent"

client.delete_agent(agent_id)
print("Agent", agent_id, "no longer exists")

configuration = ...
agent = client.create_agent(configuration, agent_id)
print("Agent", agent["id"], "has successfully been created")

context_list = ...
client.add_operations(agent_id, context_list)
print("Successfully added initial operations to agent", agent_id, "!")

decision_tree = client.get_decision_tree(agent_id, 1469476800)
print("The decision tree at timestamp", dt_timestamp, "is the following:")
print(decision_tree)

context = {
    "timezone": "+02:00",
    "timeOfDay": 7.25,
    "peopleCount": 2
}
resp = client.decide(decision_tree, context)
print("The anticipated lightbulb state is:", resp["output"]["lightbulbState"]["predicted_value"])
```

_For further information, check the ['take decision' reference documentation](#take-decision)._

### Python starter kit ###

If you prefer to get started from an existing code base, the official Python starter kit can get you there! Retrieve the sources locally and follow the "readme" to get a fully working **Wellness Coach** example using _real-world_ data.

> [:package: _Get the **craft ai** Python Starter Kit_](https://github.com/craft-ai/craft-ai-starterkit-python)

## API ##

### Project ###

**craft ai** agents belong to **projects**. In the current version, each identified users defines a owner and can create projects for themselves, in the future we will introduce shared projects.

### Configuration ###

Each agent has a configuration defining:

- the context schema, i.e. the list of property keys and their type (as defined in the following section),
- the output properties, i.e. the list of property keys on which the agent takes decisions,

> :warning: In the current version, only one output property can be provided.

- the `time_quantum`, i.e. the minimum amount of time, in seconds, that is meaningful for an agent; context updates occurring faster than this quantum won't be taken into account. As a rule of thumb, you should always choose the largest value that seems right and reduce it, if necessary, after some tests.
- the `learning_period`, i.e. the maximum amount of time, in seconds, that matters for an agent; the agent's decision model can ignore context that is older than this duration. You should generally choose the smallest value that fits this description.

> :warning: if no time_quantum is specified, the default value is 600.

> :warning: if no learning_period is specified, the default value is 15000 time quantums.

#### Context properties types ####

##### Base types: `enum` and `continuous` #####

`enum` and `continuous` are the two base **craft ai** types:

- an `enum` property is a string;
- a `continuous` property is a real number.

> :warning: the absolute value of a `continuous` property must be less than 10<sup>20</sup>.

##### Time types: `timezone`, `time_of_day`, `day_of_week`, `day_of_month` and `month_of_year` #####

**craft ai** defines the following types related to time:

- a `time_of_day` property is a real number belonging to **[0.0; 24.0[**, each value represents the number of hours in the day since midnight (e.g. 13.5 means
13:30),
- a `day_of_week` property is an integer belonging to **[0, 6]**, each
value represents a day of the week starting from Monday (0 is Monday, 6 is
Sunday).
- a `day_of_month` property is an integer belonging to **[1, 31]**, each value represents a day of the month.
- a `month_of_year` property is an integer belonging to **[1, 12]**, each value represents a month of the year.
- a `timezone` property is a string value representing the timezone as an
offset from UTC, supported format are:
  - **±[hh]:[mm]**,
  - **±[hh][mm]**,
  - **±[hh]**,
  
  where `hh` represent the hour and `mm` the minutes from UTC (eg. `+01:30`)), between `-12:00` and
  `+14:00`.
  
  Some abbreviations are also supported:
  - **UTC** or **Z** Universal Time Coordinated,
  - **GMT** Greenwich Mean Time, as UTC,
  - **BST** British Summer Time, as UTC+1 hour,
  - **IST** Irish Summer Time, as UTC+1,
  - **WET** Western Europe Time, as UTC,
  - **WEST** Western Europe Summer Time, as UTC+1,
  - **CET** Central Europe Time, as UTC+1,
  - **CEST** Central Europe Summer Time, as UTC+2,
  - **EET** Eastern Europe Time, as UTC+2,
  - **EEST** Eastern Europe Summer Time, as UTC+3,
  - **MSK** Moscow Time, as UTC+3,
  - **MSD** Moscow Summer Time, as UTC+4,
  - **AST** Atlantic Standard Time, as UTC-4,
  - **ADT** Atlantic Daylight Time, as UTC-3,
  - **EST** Eastern Standard Time, as UTC-5,
  - **EDT** Eastern Daylight Saving Time, as UTC-4,
  - **CST** Central Standard Time, as UTC-6,
  - **CDT** Central Daylight Saving Time, as UTC-5,
  - **MST** Mountain Standard Time, as UTC-7,
  - **MDT** Mountain Daylight Saving Time, as UTC-6,
  - **PST** Pacific Standard Time, as UTC-8,
  - **PDT** Pacific Daylight Saving Time, as UTC-7,
  - **HST** Hawaiian Standard Time, as UTC-10,
  - **AKST** Alaska Standard Time, as UTC-9,
  - **AKDT** Alaska Standard Daylight Saving Time, as UTC-8,
  - **AEST** Australian Eastern Standard Time, as UTC+10,
  - **AEDT** Australian Eastern Daylight Time, as UTC+11,
  - **ACST** Australian Central Standard Time, as UTC+9.5,
  - **ACDT** Australian Central Daylight Time, as UTC+10.5,
  - **AWST** Australian Western Standard Time, as UTC+8.

> :information_source: By default, the values of the `time_of_day` and `day_of_week`
> properties are generated from the [`timestamp`](#timestamp) of an agent's
> state and the agent's current `timezone`. Therefore, whenever you use generated
> `time_of_day` and/or `day_of_week` in your configuration, you **must** provide a
> `timezone` value in the context. There can only be one `timezone` property.
>
> If you wish to provide their values manually, add `is_generated: false` to the
> time types properties in your configuration. In this case, since you provide the values, the
> `timezone` property is not required, and you must update the context whenever
> one of these time values changes in a way that is significant for your system.

##### Examples #####

Let's take a look at the following configuration. It is designed to model the **color**
of a lightbulb (the `lightbulbColor` property, defined as an output) depending
on the **outside light intensity** (the `lightIntensity` property), the **time
of the day** (the `time` property) and the **day of the week** (the `day`
property).

`day` and `time` values will be generated automatically, hence the need for
`timezone`, the current Time Zone, to compute their value from given
[`timestamps`](#timestamp).

The `time_quantum` is set to 100 seconds, which means that if the lightbulb
color is changed from red to blue then from blue to purple in less that 1
minutes and 40 seconds, only the change from red to purple will be taken into
account.

The `learning_period` is set to 108 000 seconds (one month) , which means that
the state of the lightbulb from more than a month ago can be ignored when learning
the decision model.

```json
{
  "context": {
      "lightIntensity":  {
        "type": "continuous"
      },
      "time": {
        "type": "time_of_day"
      },
      "day": {
        "type": "day_of_week"
      },
      "timezone": {
        "type": "timezone"
      },
      "lightbulbColor": {
          "type": "enum"
      }
  },
  "output": ["lightbulbColor"],
  "time_quantum": 100,
  "learning_period": 108000
}
```

In this second example, the `time` property is not generated, no property of
type `timezone` is therefore needed. However values of `time` must be manually
provided continuously.

```json
{
  "context": {
    "time": {
      "type": "time_of_day",
      "is_generated": false
    },
    "lightIntensity":  {
        "type": "continuous"
    },
    "lightbulbColor": {
        "type": "enum"
    }
  },
  "output": ["lightbulbColor"],
  "time_quantum": 100,
  "learning_period": 108000
}
```

### Timestamp ###

**craft ai** API heavily relies on `timestamps`. A `timestamp` is an instant represented as a [Unix time](https://en.wikipedia.org/wiki/Unix_time), that is to say the amount of seconds elapsed since Thursday, 1 January 1970 at midnight UTC. In most programming languages this representation is easy to retrieve, you can refer to [**this page**](https://github.com/techgaun/unix-time/blob/master/README.md) to find out how.

#### `craftai.Time` ####

The `craftai.Time` class facilitates the handling of time types in **craft ai**. It is able to extract the different **craft ai** formats from various _datetime_ representations, thanks to [datetime](https://docs.python.org/3.5/library/datetime.html).

```python
# From a unix timestamp and an explicit UTC offset
t1 = craftai.Time(1465496929, "+10:00")

# t1 == {
#   utc: "2016-06-09T18:28:49.000Z",
#   timestamp: 1465496929,
#   day_of_week: 4,
#   time_of_day: 4.480277777777778,
#   timezone: "+10:00"
# }

# From a unix timestamp and using the local UTC offset.
t2 = craftai.Time(1465496929)

# Value are valid if in Paris !
# t2 == {
#   utc: "2016-06-09T18:28:49.000Z",
#   timestamp: 1465496929,
#   day_of_week: 3,
#   time_of_day: 20.480277777777776,
#   timezone: "+02:00"
# }

# From a ISO 8601 string. Note that here it should not have any ":" in the timezone part
t3 = craftai.Time("1977-04-22T01:00:00-0500")

# t3 == {
#   utc: "1977-04-22T06:00:00.000Z",
#   timestamp: 230536800,
#   day_of_week: 4,
#   time_of_day: 1,
#   timezone: "-05:00"
# }

# Retrieve the current time with the local UTC offset
now = craftai.Time()

# Retrieve the current time with the given UTC offset
nowP5 = craftai.Time(timezone="+05:00")
```

### Advanced configuration ###

The following **advanced** configuration parameters can be set in specific cases. They are **optional**. Usually you would not need them.

- `operations_as_events` is a boolean, either `true` or `false`. The default value is `false`. If it is set to true, all context operations are treated as events, as opposed to context updates. This is appropriate if the data for an agent is made of events that have no duration, and if many events are more significant than a few. If `operations_as_events` is `true`, `learning_period` and the advanced parameter `tree_max_operations` must be set as well. In that case, `time_quantum` is ignored because events have no duration, as opposed to the evolution of an agent's context over time.
- `tree_max_operations` is a positive integer. It **can and must** be set only if `operations_as_events` is `true`. It defines the maximum number of events on which a single decision tree can be based. It is complementary to `learning_period`, which limits the maximum age of events on which a decision tree is based.
- `tree_max_depth` is a positive integer. It defines the maximum depth of decision trees, which is the maximum distance between the root node and a leaf (terminal) node. A depth of 0 means that the tree is made of a single root node. By default, `tree_max_depth` is set to 6 if the output is categorical (e.g. `enum`), or to 4 if the output is numerical (e.g. `continuous`).

These advanced configuration parameters are optional, and will appear in the agent information returned by **craft ai** only if you set them to something other than their default value. If you intend to use them in a production environment, please get in touch with us.

### Agent ###

#### Create ####

Create a new agent, and create its [configuration](#configuration).

```python
client.create_agent(
    { # The configuration
        "context": {
          "peopleCount": {
            "type": "continuous"
          },
          "timeOfDay": {
            "type": "time_of_day"
          },
          "timezone": {
            "type": "timezone"
          },
          "lightbulbState": {
            "type": "enum"
          }
        },
        "output": [ "lightbulbState" ],
        "time_quantum": 100,
        "learning_period": 108000
    },
    "impervious_kraken", # id for the agent, if undefined a random id is generated
```

#### Delete ####

```python
client.delete_agent(
    "impervious_kraken" # The agent id
)
```

#### Retrieve ####

```python
client.get_agent(
    "impervious_kraken" # The agent id
)
```

#### List ####

```python
client.list_agents()
# Return a list of agents' name
# Example: [ "impervious_kraken", "joyful_octopus", ... ]

```

#### Create and retrieve shared url ####
Create and get a shareable url to view an agent tree.
Only one url can be created at a time.

```python
client.get_shared_agent_inspector_url(
    "impervious_kraken", # The agent id.
    1464600256 # optional, the timestamp for which you want to inspect the tree.
)
```

#### Delete shared url ####
Delete a shareable url.
The previous url cannot access the agent tree anymore.

```python
client.delete_shared_agent_inspector_url(
    'impervious_kraken' # The agent id.
)
```



### Context ###

#### Add operations ####

```python
client.add_operations(
    "impervious_kraken", # The agent id
    [ # The list of context operations
        {
            "timestamp": 1469410200,
            "context": {
                "timezone": "+02:00",
                "peopleCount": 0,
                "lightbulbState": "OFF"
            }
        },
        {
            "timestamp": 1469415720,
            "context": {
                "peopleCount": 1,
                "lightbulbState": "ON"
            }
        },
        {
            "timestamp": 1469416500,
            "context": {
                "peopleCount": 2
            }
        },
        {
            "timestamp": 1469417460,
            "context": {
                "lightbulbState": "OFF"
            }
        },
        {
            "timestamp": 1469419920,
            "context": {
                "peopleCount": 0
            }
        },
        {
            "timestamp": 1469460180,
            "context": {
                "peopleCount": 2
            }
        },
        {
            "timestamp": 1469471700,
            "context": {
                "lightbulbState": "ON"
            }
        },
        {
            "timestamp": 1469473560,
            "context": {
                "peopleCount": 0
            }
        }
    ]
)
```

#### List operations ####

```python
client.get_operations_list(
    "impervious_kraken", # The agent id
    1478894153, # Optional, the **start** timestamp from which the
                # operations are retrieved (inclusive bound)
    1478895266, # Optional, the **end** timestamp up to which the
                # operations are retrieved (inclusive bound)
)
```

> This call can generate multiple requests to the craft ai API as results are paginated.

#### Retrieve state ####

```python
client.get_context_state(
    "impervious_kraken", # The agent id
    1469473600 # The timestamp at which the context state is retrieved
)
```

#### Retrieve state history ####

```python
client.get_state_history(
    "impervious_kraken", # The agent id
    1478894153, # Optional, the **start** timestamp from which the
                # operations are retrieved (inclusive bound)
    1478895266, # Optional, the **end** timestamp up to which the
                # operations are retrieved (inclusive bound)
)
```

### Decision tree ###

Decision trees are computed at specific timestamps, directly by **craft ai** which learns from the context operations [added](#add-operations) throughout time.

When you [compute](#compute) a decision tree, **craft ai** returns an object containing:
- the **API version**
- the agent's configuration as specified during the agent's [creation](#create-agent)
- the tree itself as a JSON object:

  * Internal nodes are represented by a `"decision_rule"` object and a `"children"` array. The first one, contains the `"property`, and the `"property"`'s value, to decide which child matches a context.
  * Leaves have a `"predicted_value"`, `"confidence"` and `"decision_rule"` object for this value, instead of a `"children"` array. `"predicted_value`" is an estimation of the output in the contexts matching the node. `"confidence"` is a number between 0 and 1 that indicates how confident **craft ai** is that the output is a reliable prediction.  When the output is a numerical type, leaves also have a `"standard_deviation"` that indicates a margin of error around the `"predicted_value"`.
  * The root only contains a `"children"` array.

#### Compute ####

```python
client.get_decision_tree(
    "impervious_kraken", # The agent id
    1469473600 # The timestamp at which the decision tree is retrieved
)
```

#### Take decision ####

To get a chance to store and reuse the decision tree, use `get_decision_tree` and use `decide`, a simple function evaluating a decision tree offline.

```python
tree = { ... } # Decision tree as retrieved through the craft ai REST API

# Compute the decision on a fully described context
decision = client.decide(
    tree,
    { # The context on which the decision is taken
        "timezone": "+02:00",
        "timeOfDay": 7.5,
        "peopleCount": 3
    }
)

# Or Compute the decision on a context created from the given one and filling the
# `day_of_week`, `time_of_day` and `timezone` properties from the given `Time`

decision = client.decide(
  tree,
  {
    "timezone": "+02:00",
    "peopleCount": 3
  },
  craftai.Time("2010-01-01T07:30:30")
)
```

A computed `decision` on an `enum` output type would look like:

```python
{
  "context": { # In which context the decision was taken
    "timezone": "+02:00",
    "timeOfDay": 7.5,
    "peopleCount": 3
  },
  "output": { # The decision itself
    "lightbulbState": {
      "predicted_value": "ON"
      "confidence": 0.9937745256361138, # The confidence in the decision
      "decision_rules": [ # The ordered list of decision_rules that were validated to reach this decision
        {
          "property": "timeOfDay",
          "operator": ">=",
          "operand": 6
        },
        {
          "property": "peopleCount",
          "operator": ">=",
          "operand": 2
        }
      ]
    },
  }
}
```

A `decision` for a numerical output type would look like:

```python
  "output": {
    "lightbulbIntensity": {
      "predicted_value": 10.5,
      "standard_deviation": 1.25, // For numerical types, this field is returned in decisions.
      "decision_rules": [ ... ],
      "confidence": ...
    }
  }
```

A `decision` in a case where the tree cannot make a prediction:

```python
  "output": {
    "lightbulbState": {
      "predicted_value": None,
      "confidence": 0 // Zero confidence if the decision is null
      "decision_rules": [ ... ]
    }
  }
```

### Error Handling ###

When using this client, you should be careful wrapping calls to the API with `try/except` blocks, in accordance with the [EAFP](https://docs.python.org/3/glossary.html#term-eafp) principle.

The **craft ai** python client has its specific exception types, all of them inheriting from the `CraftAIError` type.

All methods which have to send an http request (all of them except `decide`) may raise either of these exceptions: `CraftAINotFoundError`, `CraftAIBadRequestError`, `CraftAICredentialsError` or `CraftAIUnknownError`.

The `decide` method only raises `CrafAIDecisionError` of `CraftAiNullDecisionError` type of exceptions. The latter is raised when no the given context is valid but no decision can be taken.

### Pandas support ###

The craft ai python client optionally supports [pandas](http://pandas.pydata.org/) a very popular library used for all things data.

Basically instead of importing the default module, you can do the following

```python
import craftai.pandas

# Most of the time you'll need the following
import numpy as np
import pandas as pd
```

The craft ai pandas module is derived for the _vanilla_ one, with the following methods are overriden to support pandas' [`DataFrame`](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html).

#### `craftai.pandas.Client.get_operations_list` #####

Retrieves the desired operations as a `DataFrame` where:

- each operation is a row,
- each context property is a column,
- the index is [_time based_](https://pandas.pydata.org/pandas-docs/stable/timeseries.html) matching the operations timestamps,
- `np.NaN` means no value were given at this property for this timestamp.

```python
df = client.get_operations_list("impervious_kraken")

# `df` is a pd.DataFrame looking like
#
#              peopleCount  lightbulbState   timezone
# 2013-01-01   0            OFF              +02:00
# 2013-01-02   1            ON               NaN
# 2013-01-03   2            NaN              NaN
# 2013-01-04   NaN          OFF              NaN
# 2013-01-05   0            NaN              NaN
```

#### `craftai.pandas.Client.add_operations` #####

Add a `DataFrame` of operations to the desired agent. The format is the same as above.

```python
df = pd.DataFrame(
  [
    [0, "OFF", "+02:00"],
    [1, "ON", np.nan],
    [2, np.nan, np.nan],
    [np.nan, "OFF", np.nan],
    [0, np.nan, np.nan]
  ],
  columns=['peopleCount', 'lightbulbState', 'timezone'],
  index=pd.date_range('20130101', periods=5, freq='D')
)
client.add_operations("impervious_kraken", df)
```

Given something that is not a `DataFrame` this method behave like the _vanilla_ `craftai.Client.add_operations`.

#### `craftai.pandas.Client.get_state_history` #####

Retrieves the desired state history as a `DataFrame` where:

- each state is a row,
- each context property is a column,
- the index is [_time based_](https://pandas.pydata.org/pandas-docs/stable/timeseries.html) matching the state timestamps

```python
df = client.get_state_history("impervious_kraken")

# `df` is a pd.DataFrame looking like
#
#              peopleCount  lightbulbState   timezone
# 2013-01-01   0            OFF              +02:00
# 2013-01-02   1            ON               +02:00
# 2013-01-03   2            ON               +02:00
# 2013-01-04   2            OFF              +02:00
# 2013-01-05   0            OFF              +02:00
```

#### `craftai.pandas.Client.decide_from_contexts_df` #####

Take multiple decisions on a given `DataFrame` following the same format as above.

```python
decisions_df = client.decide_from_contexts_df(tree, pd.DataFrame(
  [
    [0, "+02:00"],
    [1, np.nan],
    [2, np.nan],
    [np.nan, np.nan],
    [0, np.nan]
  ],
  columns=['peopleCount', 'timezone'],
  index=pd.date_range('20130101', periods=5, freq='D')
))
# `decisions_df` is a pd.DataFrame looking like
#
#              lightbulbState_predicted_value   lightbulbState_confidence ...
# 2013-01-01   OFF                              0.999449                  ...
# 2013-01-02   ON                               0.970325                  ...
# 2013-01-03   ON                               0.970325                  ...
# 2013-01-04   ON                               0.970325                  ...
# 2013-01-05   OFF                              0.999449                  ...
```

This function never raises `CraftAiNullDecisionError`, instead it inserts these errors in the result `Dataframe` in a specific `error` column.
