# YAML Skeleton
- name: step1
  action: mod#func
  args: ["input"]
  when: "${enabled} == True"
  timeout: 3
  publish: result1
  trigger: trigger1
  decorate:
    - name: timeit
      args: ["step1"]
    - step_logger

- name: step2
  on: trigger1
  action: mod#func
  args: ["${result1}"]

---

# JSON Skeleton
[
  {
    "name": "step1",
    "action": "mod#func",
    "args": ["start"],
    "timeout": 2,
    "publish": "out",
    "trigger": "go"
  },
  {
    "name": "step2",
    "on": "go",
    "action": "mod#next",
    "args": ["${out}"]
  }
]

---

# Python Dict Skeleton
[
  {
    "name": "step1",
    "action": "mod#func",
    "args": ["data"],
    "timeout": 1,
    "publish": "cleaned",
    "trigger": "next"
  },
  {
    "name": "step2",
    "on": "next",
    "action": "mod#process",
    "args": ["${cleaned}"]
  }
]
