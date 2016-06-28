setwd("~/Github/expedia-hotel-recommendations")
f = list.files("data/csv2")

tests = vector(mode="list", length=10)
preds = vector(mode="list", length=10)

for(i in 1:length(f)){
  data = read.csv(paste0("data/csv2/", f[i]))
  data = data[which(rowSums(is.na(data))==0), ]
  data = data[which(data$booking==1), ]
  train = data[which(data$year==2013), ]
  test = data[which(data$year==2014), ]
  
  train = train[, c("dist","ci_day","co_day","plan","hour",
                    "dow","stay","channel","hotel_cluster")]
  
  test = test[, c("dist","ci_day","co_day","plan","hour",
                  "dow","stay","channel","hotel_cluster")]
  
  train$channel = as.factor(train$channel)
  train$dow = as.factor(train$dow)
  train$hotel_cluster = as.factor(train$hotel_cluster)
  test$channel = as.factor(test$channel)
  test$dow = as.factor(test$dow)
  test$hotel_cluster = as.factor(test$hotel_cluster)
  
  library(randomForest)
  rf <- try(randomForest(hotel_cluster~.,
                     data=train, importance=TRUE,
                     keep.forest=TRUE, ntree=100),TRUE)
  pred = try(predict(rf, test[,-9], type="prob"),TRUE)
  pool = try(colnames(pred),TRUE)
  ans = try(t(apply(pred, 1, order, decreasing=TRUE)),TRUE)
  ans2 = try(ans[,1:5],TRUE)
  preds[[i]]=try(matrix(pool[ans2], ncol=5, byrow=FALSE),TRUE)
  tests[[i]]=try(as.character(test[,9]),TRUE)
  print(i)
}

correct = c(1,3,5,6,7,8,10)

for(i in correct){
  print(table(preds[[i]][,1] == tests[[i]])/length(tests[[i]]))
}

for(i in correct){
  a1 = as.numeric(preds[[i]][,1] == tests[[i]])
  a2 = as.numeric(preds[[i]][,2] == tests[[i]])
  a3 = as.numeric(preds[[i]][,3] == tests[[i]])
  a4 = as.numeric(preds[[i]][,4] == tests[[i]])
  a5 = as.numeric(preds[[i]][,5] == tests[[i]])
  print(mean(a1*1+a2*0.5+a3*0.333+a4*0.25+a5*0.2))
}

for(i in correct){
  data = read.csv(paste0("data/csv2/", f[i]))
  data = data[which(rowSums(is.na(data))==0), ]
  data = data[which(data$booking==1), ]
  train = data[which(data$year==2013), ]
  print(nrow(train))
}

a=rbind(preds[[1]],preds[[3]],preds[[5]],preds[[6]],preds[[7]],preds[[8]],preds[[10]])
b=c(tests[[1]],tests[[3]],tests[[5]],tests[[6]],tests[[7]],tests[[8]],tests[[10]])
table((a[,1] == b))/length(b)
a1 = as.numeric(a[,1] == b)
a2 = as.numeric(a[,2] == b)
a3 = as.numeric(a[,3] == b)
a4 = as.numeric(a[,4] == b)
a5 = as.numeric(a[,5] == b)
mean(a1*1+a2*0.5+a3*0.333+a4*0.25+a5*0.2)