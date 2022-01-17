## Overcoming Exploeation: DRL + TL in Complex and Large-Scale Env

Execute the example:

CPU:
```
python sac_modular.py --batch_size 64 --automatic_entropy_tuning True 

```

GPU:
```
python sac_modular.py --batch_size 64 --automatic_entropy_tuning True --cuda

```

To do:
Apply DNN with loss function of distance between RL-agent and goal.

