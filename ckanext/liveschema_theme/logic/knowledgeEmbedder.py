# Import libraries
import sys
import pykeen

print(sys.argv)

# Retrieve options
strModel = sys.argv[2].replace("!", "")
embedding_dim = sys.argv[3].replace("!", "")
normalization_of_entities = sys.argv[4].replace("!", "")
scoring_function = sys.argv[5].replace("!", "")
margin_loss = sys.argv[6].replace("!", "")
random_seed = sys.argv[7].replace("!", "")
num_epochs = sys.argv[8].replace("!", "")
learning_rate = sys.argv[9].replace("!", "")
batch_size = sys.argv[10].replace("!", "")
test_set_ratio = sys.argv[11].replace("!", "")
filter_negative_triples = sys.argv[12].replace("!", "")
maximum_number_of_hpo_iters = sys.argv[13].replace("!", "")

# Set path
path = "/usr/lib/ckan/default/src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/resources/" + str(sys.argv[1]) + "/"

# Create configuration
config = dict(
	training_set_path           = path + str(sys.argv[1]) + '.tsv',
	execution_mode              = 'Training_mode',
	kg_embedding_model_name     = strModel,
	embedding_dim               = int(embedding_dim),
	normalization_of_entities   = float(normalization_of_entities),  # corresponds to L2
	scoring_function            = float(scoring_function),  # corresponds to L1
	margin_loss                 = float(margin_loss),
	learning_rate               = float(learning_rate),
	batch_size                  = int(batch_size),
	num_epochs                  = int(num_epochs),
	test_set_ratio              = float(test_set_ratio),
	filter_negative_triples     = bool(filter_negative_triples),
	random_seed                 = int(random_seed),
	preferred_device            = 'gpu',
	maximum_number_of_hpo_iters = int(maximum_number_of_hpo_iters),
)

# Execute kg_embedding
results = pykeen.run(
	config=config,
	output_directory=path,
)
"""
# Create output files
with open(path+"_trained_model.txt", "w+") as res:
	res.write(str(results.trained_model)+"\n")

# Create output files
with  open(path+"_losses.txt", "w+") as res:
	res.write(str(results.losses)+"\n") 	

# Create output files
with open(path+"_evaluation_summary.txt", "w+") as res:
	res.write(str(results.evaluation_summary)+"\n")
"""