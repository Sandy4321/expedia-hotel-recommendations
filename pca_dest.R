setwd("~/Github/expedia-hotel-recommendations")

# pca dest
load("data/dest.rda")

vcm = cov(dest[ , -1])
eigs = eigen(vcm) # whose columns contain the eigenvectors

par(mfrow=c(1,2))
plot(eigs$values)
plot(cumsum(eigs$values)/sum(eigs$values), ylab="percent of total variance")

which(cumsum(eigs$values)/sum(eigs$values) >= 0.8)[1] # 16
which(cumsum(eigs$values)/sum(eigs$values) >= 0.9)[1] # 36
which(cumsum(eigs$values)/sum(eigs$values) >= 0.95)[1] # 59

new_dest = cbind(dest[,1], as.matrix(dest[,-1]) %*% eigs$vectors)
save(new_dest, file="data/new_dest.rda")