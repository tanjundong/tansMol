from models import get_model, VAE
import torch
from dataset import SmilesDataMudule
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger
import wandb
from tokenizer import SmilesTokenizer
from torch.utils.tensorboard import SummaryWriter
from pytorch_lightning.callbacks import LearningRateMonitor

tokenizer = SmilesTokenizer.load('./a.vocab')
gpus = 2
configs = {
    'hidden_dim': 768,
    'ff_dim': 512,
    'max_len': 80,
    'vocab_size': 100,
    'n_heads': 4,
    'n_encode_layers': 4,
    'n_decode_layers': 4,
    'batch_size': 16*16*2*gpus,
}
configs['vocab_size'] = tokenizer.size


wandb.init(config=configs)
configs = wandb.config
model = get_model('trans', configs)
#writer = SummaryWriter('./runs/vae')



#smiles = 'CC(=O)NC1CCC2(C)C(CCC3(C)C2C(=O)C=C2C4C(C)C(C)CCC4(C)CCC23C)C1(C)C(=O)O'
#
#token = tokenizer.smiles2ids(smiles, configs['max_len'])
#inputs = torch.LongTensor(token).unsqueeze(0)
#writer.add_graph(model, inputs)
#writer.close()


data_model = SmilesDataMudule(
    tokenizer,
    #'/data/dataset/pubsmiles/train',
    '../data/train',
    '../data/val',
    configs['batch_size'],
    configs['max_len'])


wandb_logger = WandbLogger()

wandb_logger.watch(model.model)

lr_monitor = LearningRateMonitor(logging_interval='step')
trainer = pl.Trainer(
    gpus=gpus,
    logger=wandb_logger,
    max_epochs=200,
    accelerator='dp',
    log_every_n_steps=2,
    gradient_clip_val=0.25,
    callbacks =[lr_monitor],
)

trainer.fit(model, data_model)

