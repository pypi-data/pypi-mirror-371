# BASSA: Bayesian Analysis with Spike-and-Slab Arrangements

## Overview
Most chemical datasets are small and high-dimensional, making deep learning impractical. Linear regression remains interpretable and effective, but feature selection is critical. Traditional methods pick a single “best” model, overlooking the fact that **multiple plausible models may exist**.

**BASSA** combines Bayesian **spike-and-slab regression** with a filtering method to efficiently discover and organize many valid regression models. This reveals diverse interpretations hidden in chemical data without overcommitting to a single solution.

---

## Installation
```
pip install bassa-reg
```

## Example Use
```
priors = SpikeAndSlabPriors()
config = SpikeAndSlabConfigurations(sampler_iterations=5000)
abs_dir = os.path.dirname(os.path.abspath(__file__))
regression = SpikeAndSlabRegression(x_train, y_train, priors, config, project_path=abs_dir, experiment_name="demo")
 
regression.run()

bassa = Bassa(model=regression)
bassa.run()
```

## Results
After running both the spike-and-slab regression and BASSA, results are saved in the specified project directory.<br>
The main output is the <i>bassa_plot.png</i> file, which represents the models chosen by BASSA.
<div style="text-align: center;">
<img src="images/bassa_plot.jpeg" alt="Alt text" width="500"/> <br>
</div>
This chart visualizes the different models found by BASSA, with their feature combinations and performance metrics.<br>
Key additional outputs include:<br>

### Markov Chain Visualization
<div style="text-align: center;">
<img src="images/markov_chain_visualization.png" alt="Alt text" width="800"/> <br>
</div>
The markov chain visualization shows the exploration of different models over iterations.<br>
It is sorted by feature inclusion frequency, highlighting the most commonly selected features.<br>
Precise feature inclusion frequencies are also provided in a separate file named <i>feature_stats.csv</i>.

### Survival Process Plot
The survival plot, accompanied by the <i>survival_table.csv</i> file, illustrates the survival process of models over iterations.<br>
<div style="text-align: center;">
<img src="images/survival_plot.png" alt="Alt text" width="800"/> <br>
</div>
This is an auxiliary output that helps understand how models persist or change and is used to generate the upset chart.

### Additional Data
The <i>meta_data.csv</i> file contains information about the Spike-and-Slab regression run, including the number of iterations,
and other configuration details. It also includes some metrics about the regression performance on the training data.

## Prediction on New Data
In order to make predictions on new data, create a new **TestSet** object.
```
priors = SpikeAndSlabPriors()
config = SpikeAndSlabConfigurations(sampler_iterations=5000)
abs_dir = os.path.dirname(os.path.abspath(__file__))

test_set = TestSet(x_test=x_test,
                   samples_per_y=100,
                   iterations=200,
                   y_test=y_test)

regression = SpikeAndSlabRegression(x_train,
                                    y_train,
                                    priors,
                                    config,
                                    test_set=test_set,
                                    project_path=abs_dir,
                                    experiment_name="demo")
 
regression.run()
```
The sampler will run an extra numbers of iterations set by the <i>iterations</i> parameter in the **TestSet** object.<br>
In every iteration, the sampler will sample <i>samples_per_y</i> values of y for each sample in the test set.<br>
The average of these samples will be the predicted value for each sample in the test set.<br>

## Continuing a Previous Run
In order to continue a previous run, you first need to set <i>save_samples=True</i> on the **SpikeAndSlabConfigurations** object.<br>
Then, you can load the previous run using the **SpikeAndSlabLoader** object and pass it to the **SpikeAndSlabRegression** object.<br>
```
priors = SpikeAndSlabPriors()

config = SpikeAndSlabConfigurations(sampler_iterations=5000,
                                    save_meta_data=True,
                                    save_samples=True)

abs_dir = os.path.dirname(os.path.abspath(__file__))
regression = SpikeAndSlabRegression(x=x_train,
                            y=y_train,
                            priors=priors,
                            config=config,
                            project_path=abs_dir,
                            experiment_name="example_run",)

regression.run()

# load experiment, add test set and continue for another 1000 iterations
loader = SpikeAndSlabLoader(path = f"{abs_dir}/{regression.full_experiment_name}")

regression = SpikeAndSlabRegression(x=x_train,
                                    y=y_train,
                                    priors=priors,
                                    config=config,
                                    project_path=abs_dir,
                                    experiment_name="example_run",
                                    load_experiment=loader)

regression.run()
```

## Choosing Priors
TBD

## BASSA Thresholds
TBD