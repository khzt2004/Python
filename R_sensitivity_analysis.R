library(utils)
library(tidyverse)

price <- c(200, 175, 150)
qty <- c(500, 750, 1000, 1250)

d1 <- expand.grid(price = price, qty = qty)
df <- d1 %>% 
  mutate(avg_price = round(price/qty, 2))

df_sensitivity_table <- df %>%
  mutate(qty = as.factor(paste0("qty_", qty))) %>% 
  spread(qty, avg_price)

rownames(df_sensitivity_table) <- df_sensitivity_table$price
df_sensitivity_table <- df_sensitivity_table %>% select(-price)


base_size <- 9

df_heatmap <- df %>% 
  mutate(price = as.factor(price),
         qty = as.factor(qty))

sensitivity_heatmap <- ggplot(df_heatmap, aes(price, qty)) +
  geom_tile(aes(fill = avg_price), 
            colour = "white", alpha=0.75) +
  geom_text(aes(price, qty, label = avg_price), 
            color = 'black', size = 3) +
  scale_fill_gradient(low = "white", 
                      high = "steelblue") +
  theme_grey(base_size = base_size) +
  labs(x = "price", y = "qty") +
  scale_x_discrete(expand = c(0, 0)) +
  scale_y_discrete(expand = c(0, 0)) +
  theme(
        text=element_text(size=11, color='#757575'),
        axis.ticks=element_blank(), 
        aspect.ratio = 0.9,
        axis.text.x=element_text(size=base_size*0.9,
                                 angle=330, 
                                 hjust = 0, 
                                 colour="#757575"))

sensitivity_heatmap


# -------------------balance sheet example ----------------------------------------
leather <- 5.25
ornaments <- 2.63
materials <- 0.63
labor <- 9.24
costs_licensing <- 10000
costs_employee <- 3685
costs_marketing <- 2000
qty <- 200

strategy_sensitivity <- data.frame(Strategy=c("Increase Price",
                                  "Decrease Ornament",
                                  "Break Even",
                                  "Increase Leather Price",
                                  "Increase labor expense",
                                  "Add 1000 marketing",
                                  "Decrease Price"),
                       sales_price = c(130,
                                       125,
                                       125,
                                       125,
                                       125,
                                       125,
                                       120),
                       Leather = c(leather,
                                   leather,
                                   leather,
                                   leather,
                                   leather,
                                   leather,
                                   leather),
                       Ornaments = c(ornaments,
                                     ornaments-1,
                                     ornaments,
                                     ornaments,
                                     ornaments,
                                     ornaments,
                                     ornaments),
                       Labor_expense=c(labor,
                                       labor,
                                       labor,
                                       labor,
                                       labor+1,
                                       labor,
                                       labor),
                       Materials=c(materials,
                                   materials,
                                   materials,
                                   materials,
                                   materials,
                                   materials,
                                   materials),
                       Licensing=c(costs_licensing,
                                   costs_licensing,
                                   costs_licensing,
                                   costs_licensing,
                                   costs_licensing,
                                   costs_licensing,
                                   costs_licensing),
                       Marketing=c(costs_marketing,
                                   costs_marketing,
                                   costs_marketing,
                                   costs_marketing,
                                   costs_marketing,
                                   costs_marketing + 1000,
                                   costs_marketing),
                       Employee=c(costs_employee,
                                  costs_employee,
                                  costs_employee,
                                  costs_employee,
                                  costs_employee,
                                  costs_employee,
                                  costs_employee))

strategy_sensitivity <- strategy_sensitivity %>% 
  mutate(sales_qty_to_breakeven = (Licensing + 
                                      Marketing + 
                                      Employee)/(sales_price - (Leather +
                                                                   Ornaments +
                                                                   Materials +
                                                                   Labor_expense))) %>% 
  mutate(profit_by_qty_sold = (qty*(sales_price - (Leather + 
                                                    Ornaments + 
                                                    Materials + 
                                                    Labor_expense))) - (Licensing + 
                                                                          Marketing + 
                                                                          Employee))



