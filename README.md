# BERTHAMMER

This is a pet project build around scraping and managing non-normalized data,
and seing how I can capture that data with some state-of-the-art language models.

If it works really well, the models might be useful as a tool for list building... selecting
the most under-costed units etc.


## Dev Plan
In its most grandiose form, this project will have a few phases:

1. Scrape Wahapedia's AOS Core and Faction Rules.
2. Prepare a dataset with the core and faction rules.
3. Fine-tune BERT on the new dataset
4. Explore the embeddings. Can I predict faction from the embeddings?
5. See what I can do with warscrolls. I think the points cost per unit would be an ideal target.

6. Scrape tournament data
7. Fine-tune embeddings against tournament data

It'sunlikely I'll be able to go through all of these in my spare time - 
phase 6-7 in particular may be impossible.

At least I'll learn something.

## Setup

```bash
conda env create -f setup/berthammer_cpu.yml
```

If you add any packages:


```bash
conda env export > setup/berhammer_cpu.yml
```
