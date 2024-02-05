library(ggplot2)

pca_projection <- function(orig_data_file, synth_data_file, output_png, cwd,
                           dataset_name, vars, categorical_vars) {
    options(na.action="na.pass")

    setwd(cwd)

    vars <- unlist(vars)
    categorical_vars <- unlist(categorical_vars)

    orig <- read.csv(orig_data_file)
    BioHF <- orig[,vars]

    numerical_vars <- vars[! vars %in% categorical_vars]
    BioHFHot <- data.frame(BioHF[,numerical_vars])

    for (var in categorical_vars) {
        form <- formula(paste("~", var, "-1"))
        newcols <- model.matrix(form, data=BioHF)
        BioHFHot <- data.frame(BioHFHot, newcols)
    }

    BioHFHot[numerical_vars] <- scale(BioHFHot[numerical_vars])

    PCA <- prcomp(na.omit(BioHFHot), scale = F)

    # add synth data
    synth <- read.csv(synth_data_file)
    BioHFSynth <- synth[,vars]

    BioHFSynthHot <- data.frame(BioHFSynth[,numerical_vars])
    for (var in categorical_vars) {
        form <- formula(paste("~", var, "-1"))
        newcols <- model.matrix(form, data=BioHFSynth)
        BioHFSynthHot <- data.frame(BioHFSynthHot, newcols)
    }

    BioHFSynthHot[numerical_vars] <- scale(BioHFSynthHot[numerical_vars])

    project.b <- predict(PCA, BioHFSynthHot)

    perc_var<-round(100*PCA$sdev^2/sum(PCA$sdev^2),1)

    dataGG<-data.frame(PC1=PCA$x[,1],PC2=PCA$x[,2],PC3=PCA$x[,3],PC4=PCA$x[,4],
                       type = rep("original",nrow(orig)))

    dataGG<-rbind(dataGG,data.frame(PC1=project.b[,1],PC2=project.b[,2],PC3=project.b[,3],PC4=project.b[,4],
                                    type = rep("synthetic",nrow(orig))))

    p<-qplot(PC1,PC2,data=dataGG,color=type, alpha=0.1)+theme_bw(base_size=12)+scale_colour_manual(values = c("#e41a1c","#377eb8","#4daf4a","#984ea3","#ff7f00","#ffff33","#a65628","#f781bf","#999999","black","lightgrey"))+ggtitle(dataset_name)+xlab(paste("PC1 - explaining",perc_var[1],"% of variability"))+ylab(paste("PC2 - explaining",perc_var[2],"% of variability"))

#p<-p + annotate("text", angle = 45, x = dataGG[,1], y = dataGG[,2], label = dataGG$replicate)
#exit(0)
#
    ggsave(output_png,width=10,height=10)
}
