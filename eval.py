from evaluation import start
import config

# skip_ids means to skip labels with contain "ID" .. which might be not so interesting

start.do_evaluation(skip_ids=False)
start.do_evaluation(skip_ids=True)
#start.do_evaluation(skip_ids=config.SKIP_LABELS_WITH_IDS)

