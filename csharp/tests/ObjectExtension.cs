using FluentAssertions;
using Moq;

namespace NoSuchCompany.QualityTools.Moq
{
    public static class ObjectExtension
    {
        public static TObjectType OrEquivalent<TObjectType>(this TObjectType expectedInstance)
        {
            return It.Is<TObjectType>(actualInstance => IsEquivalent(expectedInstance, actualInstance));
        }

        private static bool IsEquivalent<TObjectType>(TObjectType expectedInstance, TObjectType actualInstance)
        {
            try
            {
                actualInstance.Should().BeEquivalentTo(expectedInstance);
                return true;
            }
            catch
            {
                return false;
            }
        }
    }
}
