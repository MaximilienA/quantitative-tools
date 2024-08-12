plt.figure(figsize=(16, 6))
plt.plot(df_to_display_in_graph2.index, df_to_display_in_graph2['Upper range rate'], marker='o', linestyle='-')
plt.xlabel('Meeting dates')
plt.ylabel('Upper range rate')
plt.title('Projected FED rates for upcoming meeting dates')
plt.grid(True)

# Scale Y axis by 0.25
def make_increment(start, end, num_steps):
    return [start + i * (end - start) / (num_steps - 1) for i in range(num_steps)]

max_value = df_to_display_in_graph2['Upper range rate'].max()
min_value = df_to_display_in_graph2['Upper range rate'].min()
increment_values = make_increment(max_value+0.25, min_value-0.25, int((max_value-min_value)/0.25)+3)
plt.gca().set_yticks(increment_values)

plt.show()

st.pyplot(plt)